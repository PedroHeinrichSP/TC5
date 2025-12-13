#!/bin/bash
set -e

# Ensure PYTHONPATH is set
export PYTHONPATH=/app:$PYTHONPATH

# Run uvicorn
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
