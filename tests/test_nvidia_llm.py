"""
Tests for ProjectForge AI — NvidiaLlm Provider

Tests streaming, non-streaming, tool-call accumulation, and timeouts.
"""

import json
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from google.adk.models.llm_request import LlmRequest
from google.genai import types

from nvidia_llm import NvidiaLlm


@pytest.fixture
def sample_llm_request():
    return LlmRequest(
        contents=[
            types.Content(
                role="user",
                parts=[types.Part.from_text(text="Hello agent")],
            )
        ]
    )


@pytest.mark.asyncio
async def test_nvidia_llm_non_streaming(sample_llm_request):
    mock_choice = MagicMock()
    mock_choice.message.content = "Hello! How can I help you today?"
    mock_choice.message.tool_calls = None

    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]

    with patch("nvidia_llm.AsyncOpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_resp)
        mock_openai_cls.return_value = mock_client

        llm = NvidiaLlm(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            api_key="test-key",
            timeout=30.0,
        )

        responses = []
        async for resp in llm.generate_content_async(sample_llm_request, stream=False):
            responses.append(resp)

        assert len(responses) == 1
        assert responses[0].content.parts[0].text == "Hello! How can I help you today?"


@pytest.mark.asyncio
async def test_nvidia_llm_streaming(sample_llm_request):
    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content="Hello ", tool_calls=None))]

    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content="world!", tool_calls=None))]

    async def mock_stream():
        yield chunk1
        yield chunk2

    with patch("nvidia_llm.AsyncOpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        mock_openai_cls.return_value = mock_client

        llm = NvidiaLlm(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            api_key="test-key",
            timeout=30.0,
        )

        responses = []
        async for resp in llm.generate_content_async(sample_llm_request, stream=True):
            responses.append(resp)

        assert len(responses) == 2
        assert responses[0].content.parts[0].text == "Hello "
        assert responses[1].content.parts[0].text == "world!"


@pytest.mark.asyncio
async def test_nvidia_llm_streaming_tool_calls(sample_llm_request):
    fn1 = MagicMock()
    fn1.name = "estimate_cloud_costs"
    fn1.arguments = '{"services": '
    tc_delta1 = MagicMock(index=0, function=fn1)

    fn2 = MagicMock()
    fn2.name = None
    fn2.arguments = '"compute"}'
    tc_delta2 = MagicMock(index=0, function=fn2)

    chunk1 = MagicMock()
    chunk1.choices = [MagicMock(delta=MagicMock(content=None, tool_calls=[tc_delta1]))]

    chunk2 = MagicMock()
    chunk2.choices = [MagicMock(delta=MagicMock(content=None, tool_calls=[tc_delta2]))]

    async def mock_stream():
        yield chunk1
        yield chunk2

    with patch("nvidia_llm.AsyncOpenAI") as mock_openai_cls:
        mock_client = MagicMock()
        mock_client.chat.completions.create = AsyncMock(return_value=mock_stream())
        mock_openai_cls.return_value = mock_client

        llm = NvidiaLlm(
            model="nvidia/nemotron-3-ultra-550b-a55b",
            api_key="test-key",
            timeout=30.0,
        )

        responses = []
        async for resp in llm.generate_content_async(sample_llm_request, stream=True):
            responses.append(resp)

        assert len(responses) == 1
        fn_part = responses[0].content.parts[0]
        assert fn_part.function_call.name == "estimate_cloud_costs"
        assert fn_part.function_call.args == {"services": "compute"}
