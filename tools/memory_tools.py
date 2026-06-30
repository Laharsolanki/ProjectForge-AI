"""
ProjectForge AI — Memory Tools

Tools for persisting project context across sessions.
Uses simple JSON files in the memory/ directory.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

from config import MEMORY_DIR


def save_project_summary(project_name: str, summary: str) -> dict:
    """
    Save a project summary to persistent memory for future reference.

    This allows the agent to recall previous projects and their context
    in future sessions.

    Args:
        project_name: Name of the project (used as the storage key).
        summary: A comprehensive summary of the project including
            key decisions, tech stack, and status.

    Returns:
        A dictionary with the save status and file path.
    """
    import re

    safe_name = re.sub(r"[^\w\s-]", "", project_name).strip().lower()
    safe_name = re.sub(r"[\s]+", "-", safe_name)

    filepath = MEMORY_DIR / f"{safe_name}.json"

    # Load existing data if it exists (append to history)
    history = []
    if filepath.exists():
        try:
            existing = json.loads(filepath.read_text(encoding="utf-8"))
            history = existing.get("history", [])
        except (json.JSONDecodeError, KeyError):
            pass

    entry = {
        "timestamp": datetime.now().isoformat(),
        "summary": summary,
    }
    history.append(entry)

    data = {
        "project_name": project_name,
        "last_updated": datetime.now().isoformat(),
        "history": history,
    }

    try:
        filepath.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return {
            "status": "success",
            "filepath": str(filepath),
            "entries": len(history),
            "message": f"Project '{project_name}' saved to memory ({len(history)} entries).",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save project memory: {str(e)}",
        }


def load_project_history(project_name: str) -> dict:
    """
    Load the history and context for a previously analyzed project.

    Args:
        project_name: Name of the project to look up.

    Returns:
        A dictionary with the project history, or an error if not found.
    """
    import re

    safe_name = re.sub(r"[^\w\s-]", "", project_name).strip().lower()
    safe_name = re.sub(r"[\s]+", "-", safe_name)

    filepath = MEMORY_DIR / f"{safe_name}.json"

    if not filepath.exists():
        return {
            "status": "not_found",
            "message": f"No memory found for project '{project_name}'.",
        }

    try:
        data = json.loads(filepath.read_text(encoding="utf-8"))
        return {
            "status": "success",
            "project_name": data.get("project_name", project_name),
            "last_updated": data.get("last_updated", "unknown"),
            "entries": len(data.get("history", [])),
            "history": data.get("history", []),
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to load project memory: {str(e)}",
        }


def list_projects() -> dict:
    """
    List all projects saved in memory.

    Returns:
        A dictionary with a list of project names and their last update times.
    """
    projects = []
    for filepath in MEMORY_DIR.glob("*.json"):
        try:
            data = json.loads(filepath.read_text(encoding="utf-8"))
            projects.append({
                "project_name": data.get("project_name", filepath.stem),
                "last_updated": data.get("last_updated", "unknown"),
                "entries": len(data.get("history", [])),
            })
        except (json.JSONDecodeError, KeyError):
            projects.append({
                "project_name": filepath.stem,
                "last_updated": "error reading file",
                "entries": 0,
            })

    return {
        "status": "success",
        "count": len(projects),
        "projects": projects,
        "message": f"Found {len(projects)} project(s) in memory.",
    }
