import asyncio
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai import types
from agents import root_agent
from config import AGENT_APP_NAME, DEFAULT_USER_ID, BASE_DIR

async def main():
    db_path = BASE_DIR / "memory" / "sessions.db"
    session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{db_path}")
    session = await session_service.create_session(app_name=AGENT_APP_NAME, user_id=DEFAULT_USER_ID)
    runner = Runner(agent=root_agent, app_name=AGENT_APP_NAME, session_service=session_service)

    content = types.Content(role="user", parts=[types.Part.from_text(text="I want to build an AI resume builder")])
    async for event in runner.run_async(user_id=DEFAULT_USER_ID, session_id=session.id, new_message=content):
        print(f"--- event from: {event.author} ---")
        if event.content and event.content.parts:
            for p in event.content.parts:
                if p.text:
                    print(p.text)

asyncio.run(main())