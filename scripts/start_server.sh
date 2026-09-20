#!/usr/bin/env bash
# BharatVerse - Launch Application Server
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "=========================================================="
echo " 🇮🇳 Starting BharatVerse Resource Intelligence Server"
echo "=========================================================="

cd "$PROJECT_ROOT"

if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH=.
echo "Server starting at: http://127.0.0.1:8000"
echo "Interactive Swagger API Docs: http://127.0.0.1:8000/docs"
uvicorn backend.app.main:app --host 127.0.0.1 --port 8000 --reload
