"""
ProjectForge AI — Centralized Configuration

All configurable settings in one place. Override via environment variables.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
load_dotenv()

# ─── Paths ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent.resolve()
REPORTS_DIR = BASE_DIR / "reports"
MEMORY_DIR = BASE_DIR / "memory"
ASSETS_DIR = BASE_DIR / "assets"

# Ensure directories exist
REPORTS_DIR.mkdir(exist_ok=True)
MEMORY_DIR.mkdir(exist_ok=True)

# ─── API Keys ────────────────────────────────────────────────────────────────
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")

from google.adk.models.google_llm import Gemini
from google.genai import types as genai_types

# ─── Model Configuration ─────────────────────────────────────────────────────
# Automatic exponential backoff & retry configuration for transient 429/408/5xx errors
_RETRY_OPTIONS = genai_types.HttpRetryOptions(
    attempts=5,
    initial_delay=2.0,
    max_delay=60.0,
    exp_base=2.0,
    jitter=1.0,
)

# Strong model for orchestrator and complex reasoning
ORCHESTRATOR_MODEL = Gemini(
    model=os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-flash"),
    retry_options=_RETRY_OPTIONS,
)
# Lighter model for focused sub-agents
WORKER_MODEL = Gemini(
    model=os.getenv("WORKER_MODEL", "gemini-2.5-flash"),
    retry_options=_RETRY_OPTIONS,
)

# ─── Agent Settings ──────────────────────────────────────────────────────────
AGENT_APP_NAME = "projectforge"
DEFAULT_USER_ID = "default_user"

# ─── Web Server ──────────────────────────────────────────────────────────────
WEB_HOST = os.getenv("WEB_HOST", "127.0.0.1")
WEB_PORT = int(os.getenv("WEB_PORT", "8000"))

# ─── Feature Flags ───────────────────────────────────────────────────────────
GITHUB_ENABLED = bool(GITHUB_TOKEN)
PDF_EXPORT_ENABLED = False  # Set to True if weasyprint is installed

# ─── Stage Names (for progress tracking) ─────────────────────────────────────
STAGES = [
    "discovery",
    "tech_design",
    "report_generation",
]

STAGE_LABELS = {
    "discovery": "🔍 Discovery",
    "tech_design": "🏗️ Stack Recommendation",
    "report_generation": "📋 Report Generation",
}
