#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
[ -d .venv ] || python3 -m venv .venv
. .venv/bin/activate
pip install -q -e ".[dev]"
ruff check src tests
pytest
echo "ci-local: OK"
