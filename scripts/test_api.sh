#!/bin/bash

echo "🚀 Starting Product Metrics Copilot API..."
echo "Press Ctrl+C to stop"
echo ""
echo "API will be available at: http://localhost:8000"
echo "API docs (Swagger): http://localhost:8000/docs"
echo ""
echo "Test with:"
echo "  curl -X POST 'http://localhost:8000/analyze/quick' -F 'file=@examples/sample_timeseries.csv'"
echo ""

~/.local/bin/uv run uvicorn metrics_copilot.api:app --reload --host 0.0.0.0 --port 8000
