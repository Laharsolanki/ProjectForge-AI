"""
ProjectForge AI — Unified Entry Point

Usage:
    python main.py cli              Launch the Rich CLI interface
    python main.py web              Launch the FastAPI web server
    python main.py web --port 8080  Launch web server on custom port
    python main.py web --host 0.0.0.0  Launch web server on all interfaces
"""

from __future__ import annotations

import sys
import os

# Ensure the project root is in the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    # Force UTF-8 encoding on standard output/error to prevent UnicodeEncodeError on Windows
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    args = sys.argv[1:]

    if not args or args[0] == "cli":
        # Launch Rich CLI
        from cli import main as cli_main
        cli_main()

    elif args[0] == "web":
        # Parse optional --port and --host flags
        host = "127.0.0.1"
        port = 8000

        for i, arg in enumerate(args[1:], 1):
            if arg == "--port" and i + 1 < len(args):
                port = int(args[i + 1])
            elif arg == "--host" and i + 1 < len(args):
                host = args[i + 1]
            elif arg.startswith("--port="):
                port = int(arg.split("=")[1])
            elif arg.startswith("--host="):
                host = arg.split("=")[1]

        print(f"\n🏗️  ProjectForge AI — Web Server")
        print(f"   Starting at http://{host}:{port}")
        print(f"   Press Ctrl+C to stop\n")

        from web.app import app
        import uvicorn
        uvicorn.run(app, host=host, port=port)

    elif args[0] == "--help" or args[0] == "-h":
        print(__doc__)

    else:
        print(f"Unknown command: {args[0]}")
        print("Usage: python main.py [cli|web]")
        print("Run 'python main.py --help' for more information.")
        sys.exit(1)


if __name__ == "__main__":
    main()
