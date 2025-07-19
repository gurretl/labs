#!/bin/bash

echo "🚀 Starting MCP Strava Server..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Missing .env file. Copy .env.example to .env and configure your keys."
    exit 1
fi

# Use the configured Python environment
echo "📦 Using configured Python environment..."
PYTHON_CMD="/home/lionel/strava-mcp/.venv/bin/python"
PIP_CMD="/home/lionel/strava-mcp/.venv/bin/pip"
UVICORN_CMD="/home/lionel/strava-mcp/.venv/bin/uvicorn"

# Check if virtual environment exists
if [ ! -f "$PYTHON_CMD" ]; then
    echo "❌ Virtual environment not found. Please run: configure_python_environment first"
    exit 1
fi

echo "🌟 Starting FastAPI server..."
echo "👉 Go to http://localhost:8000 to start"
echo "👉 Then http://localhost:8000/authorize for Strava authorization"

$UVICORN_CMD server:app --reload --host 0.0.0.0 --port 8000
