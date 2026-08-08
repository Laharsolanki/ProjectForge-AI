"""
ProjectForge AI — GitHub Integration Tools

Tools for creating repos, issues, and project boards.
Requires GITHUB_TOKEN environment variable.
"""

from __future__ import annotations

import json
from config import GITHUB_TOKEN


def create_github_repo(
    name: str,
    description: str,
    private: bool = True,
) -> dict:
    """
    Create a new GitHub repository for the project.

    Args:
        name: Repository name (e.g., 'my-project').
        description: Short description of the repository.
        private: Whether the repo should be private. Defaults to True.

    Returns:
        A dictionary with the repo URL and status, or an error message.
    """
    if not GITHUB_TOKEN:
        return {
            "status": "error",
            "message": (
                "GitHub integration is not configured. "
                "Set GITHUB_TOKEN in your .env file to enable this feature."
            ),
        }

    try:
        from github import Github

        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=True,
        )
        return {
            "status": "success",
            "repo_url": repo.html_url,
            "clone_url": repo.clone_url,
            "message": f"Repository '{name}' created successfully at {repo.html_url}",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create repository: {str(e)}",
        }


def create_github_issues(
    repo_name: str,
    issues_json: str,
) -> dict:
    """
    Create GitHub issues from a list of milestone tasks.

    Args:
        repo_name: Name of the repository (e.g., 'my-project').
        issues_json: A JSON string containing a list of issues.
            Each issue should have 'title', 'body', and optionally 'labels'.
            Example: '[{"title": "Setup auth", "body": "Implement JWT auth", "labels": ["backend"]}]'

    Returns:
        A dictionary with the number of issues created and their URLs.
    """
    if not GITHUB_TOKEN:
        return {
            "status": "error",
            "message": (
                "GitHub integration is not configured. "
                "Set GITHUB_TOKEN in your .env file to enable this feature."
            ),
        }

    try:
        from github import Github

        issues_data = json.loads(issues_json)
        g = Github(GITHUB_TOKEN)
        user = g.get_user()
        repo = user.get_repo(repo_name)

        created = []
        existing_labels = {l.name for l in repo.get_labels()}

        for issue_data in issues_data:
            labels = issue_data.get("labels", [])
            # Create labels if they don't exist
            for label in labels:
                if label not in existing_labels:
                    repo.create_label(name=label, color="0366d6")
                    existing_labels.add(label)

            issue = repo.create_issue(
                title=issue_data["title"],
                body=issue_data.get("body", ""),
                labels=labels,
            )
            created.append({
                "number": issue.number,
                "title": issue.title,
                "url": issue.html_url,
            })

        return {
            "status": "success",
            "issues_created": len(created),
            "issues": created,
            "message": f"Created {len(created)} issues in {repo_name}",
        }
    except json.JSONDecodeError:
        return {
            "status": "error",
            "message": "Invalid JSON format for issues. Expected a JSON array of objects.",
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Failed to create issues: {str(e)}",
        }
