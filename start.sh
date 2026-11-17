#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"
if [ ! -d .venv ]; then python3 -m venv .venv; fi
.venv/bin/python -m pip install -r requirements.txt
if [ ! -f .env ]; then .venv/bin/python scripts/bootstrap.py; fi
printf '\nOpen http://127.0.0.1:8000 in your browser\n'
exec .venv/bin/python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
