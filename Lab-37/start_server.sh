#!/bin/bash

echo "🚀 Starting Strava MCP System..."
echo "📦 Using configured Python environment..."
echo "🏃‍♂️ MCP Version: Model Context Protocol"
echo ""
echo "🛠️  Available MCP Tools:"
echo "   - get_activities: Retrieve Strava activities (2022-2025)"
echo "   - get_activity_stats: Get summary statistics"
echo ""
echo "🔐 OAuth2 Flow: Automatic token management"
echo "   • First run: Browser authorization will open automatically"
echo "   • Future runs: Tokens refresh automatically"
echo ""
echo "🤖 Starting MCP-enabled Strava Chatbot..."
echo "📡 The chatbot will automatically start the MCP server and connect to it."
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Missing .env file. Copy .env.example to .env and configure your keys."
    exit 1
fi

# Check if virtual environment exists
if [ -f ".venv/bin/python" ]; then
    PYTHON_CMD=".venv/bin/python"
elif [ -f "venv/bin/python" ]; then
    PYTHON_CMD="venv/bin/python"
else
    echo "❌ Virtual environment not found. Please create it first:"
    echo "python -m venv .venv"
    echo "source .venv/bin/activate"
    echo "pip install -r requirements.txt"
    exit 1
fi

echo "📦 Using configured Python environment..."
echo "� MCP Version: Model Context Protocol"
echo ""
echo "🛠️  Available MCP Tools:"
echo "   - get_activities: Retrieve Strava activities (2024-2025)"
echo "   - get_activity_stats: Get summary statistics"
echo ""
echo "🤖 Starting MCP-enabled Strava Chatbot..."
echo "� The chatbot will automatically start the MCP server and connect to it."
echo ""

# Start the MCP chatbot (which will start its own MCP server)
$PYTHON_CMD strava_chatbot.py
