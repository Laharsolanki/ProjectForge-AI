"""
ProjectForge AI — Rich CLI Interface

Interactive terminal UI with stage progress, formatted responses,
and special commands.
"""

from __future__ import annotations

import asyncio
import sys

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.prompt import Prompt
from rich.table import Table
from rich.text import Text
from rich.theme import Theme
from rich import box

from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService

from config import (
    AGENT_APP_NAME,
    DEFAULT_USER_ID,
    STAGES,
    STAGE_LABELS,
    BASE_DIR,
)
from agents import root_agent

# ─── Theme ────────────────────────────────────────────────────────────────────
custom_theme = Theme({
    "info": "cyan",
    "success": "bold green",
    "warning": "bold yellow",
    "error": "bold red",
    "stage": "bold magenta",
    "brand": "bold blue",
})

console = Console(theme=custom_theme)

# ─── Banner ───────────────────────────────────────────────────────────────────
BANNER = r"""
[bold blue]
  ╔═══════════════════════════════════════════════════════════╗
  ║                                                           ║
  ║   ██████╗ ██████╗  ██████╗      ██╗███████╗ ██████╗████╗  ║
  ║   ██╔══██╗██╔══██╗██╔═══██╗     ██║██╔════╝██╔═══██╔══██╗ ║
  ║   ██████╔╝██████╔╝██║   ██║     ██║█████╗  ██║   ████╔═╝  ║
  ║   ██╔═══╝ ██╔══██╗██║   ██║██   ██║██╔══╝  ██║   ██╔══╝   ║
  ║   ██║     ██║  ██║╚██████╔╝╚█████╔╝███████╗╚██████╔╝      ║
  ║   ╚═╝     ╚═╝  ╚═╝ ╚═════╝  ╚════╝ ╚══════╝ ╚═════╝      ║
  ║                                                           ║
  ║          [bold cyan]ProjectForge AI[/bold cyan] — Software Architect Agent        ║
  ║                                                           ║
  ╚═══════════════════════════════════════════════════════════╝
[/bold blue]
"""

HELP_TEXT = """
[bold]Available Commands:[/bold]
  [cyan]/help[/cyan]     — Show this help message
  [cyan]/save[/cyan]     — Save current project to memory
  [cyan]/history[/cyan]  — Show project history
  [cyan]/export[/cyan]   — Export the report (after generation)
  [cyan]/stage[/cyan]    — Show current stage progress
  [cyan]/clear[/cyan]    — Clear the screen
  [cyan]/quit[/cyan]     — Exit ProjectForge AI
"""


def show_stage_progress(current_stage: str | None) -> None:
    """Display a visual stage progress indicator."""
    table = Table(
        title="📊 Project Analysis Progress",
        box=box.ROUNDED,
        show_header=False,
        padding=(0, 2),
    )
    table.add_column("Stage", style="bold")
    table.add_column("Status")

    for stage in STAGES:
        label = STAGE_LABELS.get(stage, stage)
        if current_stage is None:
            status = "⬜ Pending"
            style = "dim"
        elif stage == current_stage:
            status = "🔵 In Progress"
            style = "bold cyan"
        elif STAGES.index(stage) < STAGES.index(current_stage):
            status = "✅ Complete"
            style = "green"
        else:
            status = "⬜ Pending"
            style = "dim"
        table.add_row(Text(label, style=style), Text(status, style=style))

    console.print(table)
    console.print()


async def run_cli() -> None:
    """Main CLI loop."""
    console.print(BANNER)
    console.print(
        Panel(
            "[bold]Welcome to ProjectForge AI![/bold]\n\n"
            "I'm your senior software architect. Tell me about your project idea, "
            "and I'll help you design a complete, production-ready solution.\n\n"
            "Type [cyan]/help[/cyan] for commands, or just start describing your project.",
            border_style="blue",
            padding=(1, 2),
        )
    )
    console.print()

    # Initialize session service with SQLite for persistence
    db_path = BASE_DIR / "memory" / "sessions.db"
    session_service = DatabaseSessionService(db_url=f"sqlite:///{db_path}")

    runner = Runner(
        agent=root_agent,
        app_name=AGENT_APP_NAME,
        session_service=session_service,
    )

    # Create a new session
    session = await session_service.create_session(
        app_name=AGENT_APP_NAME,
        user_id=DEFAULT_USER_ID,
    )
    session_id = session.id

    current_stage = None

    while True:
        try:
            user_input = Prompt.ask("\n[bold green]You[/bold green]")
        except (KeyboardInterrupt, EOFError):
            console.print("\n[info]Goodbye! 👋[/info]")
            break

        if not user_input.strip():
            continue

        # ─── Handle commands ──────────────────────────────────────────
        cmd = user_input.strip().lower()

        if cmd == "/quit" or cmd == "/exit":
            console.print("[info]Goodbye! Thanks for using ProjectForge AI. 👋[/info]")
            break

        if cmd == "/help":
            console.print(Panel(HELP_TEXT, title="Help", border_style="cyan"))
            continue

        if cmd == "/stage":
            show_stage_progress(current_stage)
            continue

        if cmd == "/clear":
            console.clear()
            console.print(BANNER)
            continue

        if cmd == "/history":
            from tools.memory_tools import list_projects
            result = list_projects()
            if result["count"] == 0:
                console.print("[dim]No projects in memory yet.[/dim]")
            else:
                table = Table(title="📁 Project History", box=box.ROUNDED)
                table.add_column("Project", style="cyan")
                table.add_column("Last Updated", style="dim")
                table.add_column("Sessions", justify="center")
                for p in result["projects"]:
                    table.add_row(
                        p["project_name"],
                        p["last_updated"][:19],
                        str(p["entries"]),
                    )
                console.print(table)
            continue

        if cmd == "/save":
            user_input = "Please save the current project to memory using the save_project_summary tool."

        if cmd == "/export":
            user_input = (
                "Please generate the final report now using the Report Generator agent, "
                "and save it using the save_report tool."
            )

        # ─── Send to agent ────────────────────────────────────────────
        console.print()

        from google.genai import types

        user_content = types.Content(
            role="user",
            parts=[types.Part.from_text(text=user_input)],
        )

        full_response = ""

        with Progress(
            SpinnerColumn(),
            TextColumn("[bold cyan]ProjectForge AI is thinking..."),
            console=console,
            transient=True,
        ) as progress:
            progress.add_task("thinking", total=None)

            async for event in runner.run_async(
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
                new_message=user_content,
            ):
                # Collect text from agent responses
                if event.content and event.content.parts:
                    for part in event.content.parts:
                        if part.text:
                            full_response += part.text

        # Display the response
        if full_response.strip():
            console.print(
                Panel(
                    Markdown(full_response),
                    title="[bold blue]🏗️ ProjectForge AI[/bold blue]",
                    border_style="blue",
                    padding=(1, 2),
                )
            )

        # Update stage from session state
        try:
            updated_session = await session_service.get_session(
                app_name=AGENT_APP_NAME,
                user_id=DEFAULT_USER_ID,
                session_id=session_id,
            )
            if updated_session and updated_session.state:
                current_stage = updated_session.state.get("current_stage", current_stage)
        except Exception:
            pass


def main() -> None:
    """Entry point for the CLI."""
    try:
        asyncio.run(run_cli())
    except KeyboardInterrupt:
        console.print("\n[info]Goodbye! 👋[/info]")
        sys.exit(0)


if __name__ == "__main__":
    main()
