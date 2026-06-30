"""
ProjectForge AI — Report Tools

Tools for saving and exporting project reports.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from config import REPORTS_DIR


def save_report(content: str, project_name: str) -> dict:
    """
    Save a project report as a Markdown file to the reports directory.

    Args:
        content: The full Markdown content of the report.
        project_name: Name of the project (used for the filename).

    Returns:
        A dictionary with the file path and status.
    """
    # Sanitize project name for filename
    safe_name = re.sub(r"[^\w\s-]", "", project_name).strip().lower()
    safe_name = re.sub(r"[\s]+", "-", safe_name)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"{safe_name}-{timestamp}.md"
    filepath = REPORTS_DIR / filename

    try:
        filepath.write_text(content, encoding="utf-8")
        return {
            "status": "success",
            "filepath": str(filepath),
            "filename": filename,
            "message": f"Report saved to {filepath}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to save report: {str(e)}",
        }


def generate_mermaid_diagram(description: str) -> dict:
    """
    Generate a Mermaid diagram code block from an architecture description.

    The agent should provide a textual description of the architecture,
    and this tool will format it as a Mermaid-compatible diagram string
    that can be embedded in Markdown reports.

    Args:
        description: A textual description of the architecture components
            and their relationships. The agent should structure this as
            Mermaid syntax (e.g., 'graph TD; A-->B; B-->C').

    Returns:
        A dictionary containing the formatted Mermaid code block.
    """
    # Ensure the diagram starts with a valid Mermaid directive
    description = description.strip()
    valid_starts = ("graph ", "flowchart ", "sequenceDiagram", "classDiagram",
                    "stateDiagram", "erDiagram", "gantt", "pie ", "gitgraph")

    has_valid_start = any(description.startswith(s) for s in valid_starts)

    if not has_valid_start:
        # Default to a flowchart if no directive is provided
        description = f"graph TD\n{description}"

    mermaid_block = f"```mermaid\n{description}\n```"

    return {
        "status": "success",
        "mermaid_code": mermaid_block,
        "raw_diagram": description,
        "message": "Mermaid diagram generated. Embed the 'mermaid_code' in your report.",
    }
