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
NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY", "")
NVIDIA_BASE_URL = os.getenv("NVIDIA_BASE_URL", "https://integrate.api.nvidia.com/v1")
NVIDIA_MODEL = os.getenv("NVIDIA_MODEL", "nvidia/nemotron-3-ultra-550b-a55b")
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "nvidia" if NVIDIA_API_KEY else "gemini")

# ─── Model Configuration ─────────────────────────────────────────────────────
if LLM_PROVIDER == "nvidia" and NVIDIA_API_KEY:
    from nvidia_llm import NvidiaLlm

    ORCHESTRATOR_MODEL = NvidiaLlm(
        model=NVIDIA_MODEL,
        api_key=NVIDIA_API_KEY,
        base_url=NVIDIA_BASE_URL,
        temperature=0.7,
        max_tokens=4096,
    )
    WORKER_MODEL = NvidiaLlm(
        model=NVIDIA_MODEL,
        api_key=NVIDIA_API_KEY,
        base_url=NVIDIA_BASE_URL,
        temperature=0.7,
        max_tokens=4096,
    )
else:
    from google.adk.models.google_llm import Gemini
    from google.genai import types as genai_types

    _RETRY_OPTIONS = genai_types.HttpRetryOptions(
        attempts=5,
        initial_delay=2.0,
        max_delay=60.0,
        exp_base=2.0,
        jitter=1.0,
    )

    ORCHESTRATOR_MODEL = Gemini(
        model=os.getenv("ORCHESTRATOR_MODEL", "gemini-2.5-flash"),
        retry_options=_RETRY_OPTIONS,
    )
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
