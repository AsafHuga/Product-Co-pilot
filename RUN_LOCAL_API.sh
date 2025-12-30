#!/bin/bash

echo "🚀 Starting Local API Server..."
echo ""
echo "This will run the API on http://localhost:8000"
echo "Update your frontend to use: const API_URL = 'http://localhost:8000'"
echo ""
echo "Press Ctrl+C to stop"
echo ""

cd /Users/asafhuga
~/.local/bin/uv run uvicorn metrics_copilot.api:app --host 0.0.0.0 --port 8000 --reload
