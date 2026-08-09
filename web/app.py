"""
ProjectForge AI — FastAPI Web Server

REST API + WebSocket for the web UI.
Serves the chat interface and handles agent communication.
"""

from __future__ import annotations

import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types

from config import (
    AGENT_APP_NAME,
    DEFAULT_USER_ID,
    REPORTS_DIR,
    BASE_DIR,
)
from agents import root_agent

# ─── Paths ────────────────────────────────────────────────────────────────────
WEB_DIR = Path(__file__).parent
TEMPLATES_DIR = WEB_DIR / "templates"
STATIC_DIR = WEB_DIR / "static"

# ─── Global state ─────────────────────────────────────────────────────────────
session_service = None
runner = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup."""
    global session_service, runner

    db_path = BASE_DIR / "memory" / "sessions.db"
    session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{db_path}")

    runner = Runner(
        agent=root_agent,
        app_name=AGENT_APP_NAME,
        session_service=session_service,
    )

    yield

    # Cleanup if needed
    pass


# ─── App ──────────────────────────────────────────────────────────────────────
app = FastAPI(
    title="ProjectForge AI",
    description="Professional Software Architect Agent",
    version="1.0.0",
    lifespan=lifespan,
)

# Mount static files
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

# Templates
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))


# ─── Routes ───────────────────────────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main chat UI."""
    return templates.TemplateResponse(request, "index.html")


@app.post("/api/session")
async def create_session():
    """Create a new chat session."""
    session = await session_service.create_session(
        app_name=AGENT_APP_NAME,
        user_id=DEFAULT_USER_ID,
    )
    return {"session_id": session.id}


@app.get("/api/reports")
async def list_reports():
    """List all generated reports."""
    reports = []
    for f in REPORTS_DIR.glob("*.md"):
        reports.append({
            "filename": f.name,
            "size_bytes": f.stat().st_size,
            "modified": f.stat().st_mtime,
        })
    reports.sort(key=lambda x: x["modified"], reverse=True)
    return {"reports": reports}


@app.get("/api/reports/{filename}")
async def download_report(filename: str):
    """Download a specific report."""
    filepath = REPORTS_DIR / filename
    if not filepath.exists() or not filepath.is_file():
        return JSONResponse(
            status_code=404,
            content={"error": "Report not found"},
        )
    return FileResponse(
        path=str(filepath),
        filename=filename,
        media_type="text/markdown",
    )


@app.websocket("/ws/{session_id}")
async def websocket_chat(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for real-time chat with the agent.
    Streams agent responses as they are generated.
    """
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)
            user_text = message.get("text", "").strip()

            if not user_text:
                continue

            # Create user content
            user_content = types.Content(
                role="user",
                parts=[types.Part.from_text(text=user_text)],
            )

            # Stream agent response
            full_response = ""

            try:
                async for event in runner.run_async(
                    user_id=DEFAULT_USER_ID,
                    session_id=session_id,
                    new_message=user_content,
                ):
                    # Filter to only the root orchestrator's conversational events
                    if event.author and event.author != root_agent.name:
                        continue
                    if event.content and event.content.parts:
                        for part in event.content.parts:
                            if part.text:
                                full_response += part.text
                                # Send incremental chunks
                                await websocket.send_json({
                                    "type": "chunk",
                                    "text": part.text,
                                    "agent": event.author or "projectforge",
                                })

                # Signal completion
                current_stage = "discovery"
                try:
                    updated_session = await session_service.get_session(
                        app_name=AGENT_APP_NAME,
                        user_id=DEFAULT_USER_ID,
                        session_id=session_id,
                    )
                    if updated_session and updated_session.state:
                        state = updated_session.state
                        discovery_state = state.get("discovery_report")
                        discovery_ready = False
                        if isinstance(discovery_state, dict):
                            discovery_ready = discovery_state.get("status") == "ready" or "high" in str(discovery_state.get("confidence", "")).lower()
                        elif isinstance(discovery_state, str):
                            discovery_ready = "confidence: high" in discovery_state.lower() or "confidence:** high" in discovery_state.lower() or '"confidence": "high"' in discovery_state.lower() or "discovery report summary" in discovery_state.lower()
                        elif hasattr(discovery_state, "status"):
                            discovery_ready = getattr(discovery_state, "status") == "ready"

                        if "final_report" in state:
                            current_stage = "report_generation"
                        elif "tech_design" in state:
                            current_stage = "report_generation"
                        elif discovery_ready:
                            current_stage = "tech_design"
                        else:
                            current_stage = "discovery"

                        # Persist back to sqlite
                        import sqlite3
                        db_path = BASE_DIR / "memory" / "sessions.db"
                        state["current_stage"] = current_stage
                        conn = sqlite3.connect(db_path)
                        try:
                            cursor = conn.cursor()
                            cursor.execute(
                                "UPDATE sessions SET state = ? WHERE id = ?",
                                (json.dumps(state), session_id)
                            )
                            conn.commit()
                        finally:
                            conn.close()
                except Exception:
                    pass

                await websocket.send_json({
                    "type": "done",
                    "full_text": full_response,
                    "current_stage": current_stage,
                })

            except Exception as e:
                await websocket.send_json({
                    "type": "error",
                    "message": f"Agent error: {str(e)}",
                })

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({
                "type": "error",
                "message": f"Connection error: {str(e)}",
            })
        except Exception:
            pass


def start_server(host: str = "127.0.0.1", port: int = 8000):
    """Start the FastAPI server."""
    import uvicorn
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    start_server()
