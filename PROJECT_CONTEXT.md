# PROJECT_CONTEXT.md — Developer Onboarding Guide
> ⚠️ **PRIVATE FILE** — Do NOT upload this to GitHub. Add to `.gitignore` if needed.

## Project Name
**ProjectForge AI** — Multi-Agent Software Architect

## Objective
Build an AI-powered software architect that takes a vague project idea and produces a professional, shareable project document through structured multi-stage analysis.

## Summary
ProjectForge AI uses Google's Agent Development Kit (ADK) to orchestrate 5 specialized Gemini-powered agents through a 5-stage workflow: Discovery → Technical Design → Risk Analysis → Learning Path → Report Generation. It features a Rich-powered CLI and a FastAPI web interface with WebSocket streaming, session persistence via SQLite, and custom tools for cost estimation, GitHub integration, and memory.

## Architecture
```
Master Orchestrator (gemini-2.5-pro)
├── Discovery Agent (gemini-2.5-flash) — Understands the real problem
├── Technical Design Agent (gemini-2.5-pro) — Architecture + tech stack
├── Risk Analysis Agent (gemini-2.5-flash) — Failure modes + mitigations
└── Report Generator Agent (gemini-2.5-flash) — Final Markdown document
```
Communication: ADK sub_agents delegation + session.state sharing + SQLite persistence

## Agent Responsibilities
| Agent | Input | Output |
|---|---|---|
| Orchestrator | User messages | Routes to correct sub-agent |
| Discovery | Project idea | Discovery Report (problem, users, metrics) |
| Tech Design | Discovery Report | Architecture, tech stack, DB schema, API, milestones |
| Risk Analysis | Discovery + Design | 5-10 specific risks with mitigations |
| Report Generator | All previous outputs | Professional Markdown document |

## Folder Structure
```
agents/          — ADK LlmAgent definitions
prompts/         — System prompt strings
tools/           — Custom FunctionTools
web/             — FastAPI + HTML/CSS/JS
tests/           — pytest unit tests
memory/          — JSON project persistence
reports/         — Generated Markdown reports
config.py        — Centralized configuration
models.py        — Pydantic data models
cli.py           — Rich terminal interface
main.py          — Entry point
```

## Technology Stack
- **Runtime**: Python 3.13
- **AI Framework**: Google ADK 2.3.0
- **LLM**: Google Gemini (2.5-pro + 2.5-flash)
- **Web**: FastAPI + vanilla HTML/JS
- **CLI**: Rich library
- **Data**: Pydantic v2, SQLite (sessions), JSON (memory)
- **Testing**: pytest

## APIs Used
1. **Google Gemini API** (required) — Powers all agents
2. **GitHub API** (optional) — Repo/issue creation via PyGithub

## Environment Variables
```
GOOGLE_API_KEY=       # Required — Gemini API key
GITHUB_TOKEN=         # Optional — GitHub PAT
ORCHESTRATOR_MODEL=   # Optional — default: gemini-2.5-pro
WORKER_MODEL=         # Optional — default: gemini-2.5-flash
WEB_HOST=             # Optional — default: 127.0.0.1
WEB_PORT=             # Optional — default: 8000
```

## Important Config Files
- `.env` — API keys (never commit)
- `config.py` — All settings
- `requirements.txt` — Python dependencies

## How to Run
```bash
# CLI mode
python main.py cli

# Web mode
python main.py web

# ADK dev tools
adk web agents

# Tests
python -m pytest tests/ -v
```

## Current Status
- ✅ All 5 agents implemented
- ✅ 4 custom tools implemented
- ✅ CLI interface complete
- ✅ Web interface complete
- ✅ 28/28 unit tests passing
- ✅ All dependencies installed
- ⏳ Live agent testing (needs API key)

## Known Issues
1. Pydantic models defined but not used for structured output (agents output free text)
2. No auth on web UI
3. No timeout on agent execution
4. No logging framework (errors silently caught)

## Future Improvements
1. Use `output_schema` for structured agent responses
2. Add agent callbacks for programmatic stage tracking
3. Add web UI authentication
4. PDF export support
5. Project comparison feature
6. Code scaffolding from design documents

## Common Troubleshooting
| Issue | Fix |
|---|---|
| `401 Unauthorized` | Check GOOGLE_API_KEY in `.env` |
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| `Address already in use` | Stop other server or use `--port 8001` |
| CLI crashes on start | Ensure `.env` exists with valid key |
| Agent doesn't respond | Check internet connection + API quota |
