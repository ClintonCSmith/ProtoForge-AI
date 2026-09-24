#!/usr/bin/env bash
# Start the ProtoForge AI backend (FastAPI) on port 8000.
# Run from anywhere:  backend/run_server.sh
# Logs: /tmp/protoforge-backend.log
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
VENV_PY="$REPO_ROOT/backend/venv/bin/python"

if [ ! -x "$VENV_PY" ]; then
  echo "ERROR: virtualenv not found at $VENV_PY — create it with:"
  echo "  python3 -m venv $REPO_ROOT/backend/venv"
  echo "  $VENV_PY -m pip install -r $REPO_ROOT/backend/requirements.txt"
  exit 1
fi

# Stop any existing instance on port 8000
if command -v fuser >/dev/null 2>&1; then
  fuser -k 8000/tcp 2>/dev/null || true
else
  pkill -f "uvicorn backend.main" 2>/dev/null || true
fi
sleep 1

# Start detached (survives shell exit)
cd "$REPO_ROOT"
setsid nohup "$VENV_PY" -m uvicorn backend.main:app \
  --host 0.0.0.0 --port 8000 --log-level info \
  > /tmp/protoforge-backend.log 2>&1 &

echo "Backend starting on http://0.0.0.0:8000 — log: /tmp/protoforge-backend.log"
sleep 3
curl -s -m 5 http://localhost:8000/health && echo