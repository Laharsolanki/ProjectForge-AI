"""
ProjectForge AI — NVIDIA & OpenAI-Compatible LLM Provider for Google ADK

Allows Google ADK agents to use NVIDIA NIM models (such as Nemotron)
via the OpenAI-compatible API endpoint.
"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, AsyncGenerator, Dict, List, Optional

from google.adk.models.base_llm import BaseLlm
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.genai import types
from openai import AsyncOpenAI
from pydantic import Field

logger = logging.getLogger("projectforge.nvidia_llm")


class NvidiaLlm(BaseLlm):
    """Google ADK BaseLlm implementation for NVIDIA NIM / OpenAI-compatible models."""

    model: str = "nvidia/nemotron-3-ultra-550b-a55b"
    api_key: str = Field(default="")
    base_url: str = Field(default="https://integrate.api.nvidia.com/v1")
    temperature: float = 0.7
    max_tokens: int = 4096
    timeout: float = 60.0

    async def generate_content_async(
        self, llm_request: LlmRequest, stream: bool = False
    ) -> AsyncGenerator[LlmResponse, None]:
        client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            timeout=self.timeout,
        )

        messages = []

        # 1. System instruction
        if llm_request.config and llm_request.config.system_instruction:
            sys_text = ""
            if isinstance(llm_request.config.system_instruction, str):
                sys_text = llm_request.config.system_instruction
            elif hasattr(llm_request.config.system_instruction, "parts"):
                sys_text = "".join(
                    p.text for p in llm_request.config.system_instruction.parts if hasattr(p, "text") and p.text
                )
            if sys_text:
                messages.append({"role": "system", "content": sys_text})

        # 2. History & Contents
        for content in llm_request.contents:
            role = "assistant" if content.role in ("model", "assistant") else "user"
            
            tool_calls = []
            tool_responses = []
            text_parts = []

            for part in (content.parts or []):
                if hasattr(part, "function_response") and part.function_response:
                    resp_dict = part.function_response.response or {}
                    tool_responses.append({
                        "role": "tool",
                        "tool_call_id": part.function_response.name,
                        "name": part.function_response.name,
                        "content": json.dumps(resp_dict) if isinstance(resp_dict, dict) else str(resp_dict),
                    })
                elif hasattr(part, "function_call") and part.function_call:
                    tool_calls.append({
                        "id": part.function_call.name,
                        "type": "function",
                        "function": {
                            "name": part.function_call.name,
                            "arguments": json.dumps(part.function_call.args or {}),
                        }
                    })
                elif hasattr(part, "text") and part.text:
                    text_parts.append(part.text)

            if tool_calls:
                msg_dict = {"role": "assistant", "tool_calls": tool_calls}
                if text_parts:
                    msg_dict["content"] = "\n".join(text_parts)
                messages.append(msg_dict)
            elif text_parts:
                messages.append({"role": role, "content": "\n".join(text_parts)})

            for tr in tool_responses:
                messages.append(tr)

        # Ensure we have at least one message
        if not messages:
            messages.append({"role": "user", "content": "Hello"})

        # 3. Tools conversion
        tools = []
        if llm_request.config and llm_request.config.tools:
            for t in llm_request.config.tools:
                if hasattr(t, "function_declarations") and t.function_declarations:
                    for fd in t.function_declarations:
                        schema = {"type": "object", "properties": {}}
                        if hasattr(fd, "parameters") and fd.parameters:
                            if hasattr(fd.parameters, "properties") and fd.parameters.properties:
                                for k, v in fd.parameters.properties.items():
                                    t_type = "string"
                                    if hasattr(v, "type"):
                                        t_type = str(v.type).lower().replace("type.", "")
                                    schema["properties"][k] = {
                                        "type": t_type,
                                        "description": getattr(v, "description", "") or "",
                                    }
                            if hasattr(fd.parameters, "required") and fd.parameters.required:
                                schema["required"] = list(fd.parameters.required)
                        tools.append({
                            "type": "function",
                            "function": {
                                "name": fd.name,
                                "description": fd.description or "",
                                "parameters": schema,
                            }
                        })

        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }
        if tools:
            kwargs["tools"] = tools

        start_time = time.perf_counter()
        try:
            if stream:
                kwargs["stream"] = True
                stream_resp = await client.chat.completions.create(**kwargs)
                tool_calls_accumulator: Dict[int, Dict[str, str]] = {}

                async for chunk in stream_resp:
                    if not chunk.choices:
                        continue
                    delta = chunk.choices[0].delta

                    # Handle streamed text
                    if delta.content:
                        part = types.Part.from_text(text=delta.content)
                        yield LlmResponse(content=types.Content(role="model", parts=[part]))

                    # Accumulate streamed tool calls
                    if delta.tool_calls:
                        for tc in delta.tool_calls:
                            idx = tc.index
                            if idx not in tool_calls_accumulator:
                                tool_calls_accumulator[idx] = {
                                    "name": tc.function.name or "",
                                    "arguments": tc.function.arguments or "",
                                }
                            else:
                                if tc.function.name:
                                    tool_calls_accumulator[idx]["name"] += tc.function.name
                                if tc.function.arguments:
                                    tool_calls_accumulator[idx]["arguments"] += tc.function.arguments

                # Emit accumulated tool calls if any were made
                if tool_calls_accumulator:
                    parts = []
                    for _, tc in sorted(tool_calls_accumulator.items()):
                        args = {}
                        try:
                            args = json.loads(tc["arguments"]) if tc["arguments"] else {}
                        except Exception:
                            pass
                        parts.append(types.Part.from_function_call(name=tc["name"], args=args))
                    yield LlmResponse(content=types.Content(role="model", parts=parts))

                elapsed = time.perf_counter() - start_time
                logger.info("NVIDIA LLM streamed request [%s] completed in %.2fs", self.model, elapsed)
            else:
                resp = await client.chat.completions.create(**kwargs)
                choice = resp.choices[0]
                msg = choice.message

                parts = []
                if msg.tool_calls:
                    for tc in msg.tool_calls:
                        args = {}
                        try:
                            args = json.loads(tc.function.arguments) if tc.function.arguments else {}
                        except Exception:
                            pass
                        parts.append(types.Part.from_function_call(name=tc.function.name, args=args))
                if msg.content:
                    parts.append(types.Part.from_text(text=msg.content))

                if not parts:
                    parts.append(types.Part.from_text(text=""))

                elapsed = time.perf_counter() - start_time
                logger.info("NVIDIA LLM request [%s] completed in %.2fs", self.model, elapsed)
                content_resp = types.Content(role="model", parts=parts)
                yield LlmResponse(content=content_resp)

        except Exception as e:
            elapsed = time.perf_counter() - start_time
            logger.error("NVIDIA LLM error after %.2fs: %s", elapsed, str(e), exc_info=True)
            error_content = types.Content(
                role="model",
                parts=[types.Part.from_text(text=f"Error communicating with NVIDIA model: {str(e)}")]
            )
            yield LlmResponse(content=error_content)
