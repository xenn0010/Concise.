#!/bin/bash

# Concise SDK v1.1.0 Demo - Startup Script

echo "=========================================="
echo "Concise SDK v1.1.0 - Live Demo"
echo "=========================================="
echo ""

# Check if backend is running
echo "Checking Concise backend..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend is running on port 8000"
else
    echo "✗ Backend is NOT running on port 8000"
    echo "  Please start it with:"
    echo "  cd /home/yab/Concise/backend && source venv/bin/activate && uvicorn app.main:app --host 0.0.0.0 --port 8000"
    exit 1
fi

# Load environment
cd /home/yab/Concise/demo
source venv/bin/activate

# Check .env file
if [ ! -f .env ]; then
    echo "✗ .env file not found, using defaults"
    export CONCISE_API_URL="http://localhost:8000"
    export CONCISE_API_KEY="demo-key-12345"
else
    echo "✓ Loading environment from .env"
    export $(cat .env | grep -v '^#' | xargs)
fi

echo ""
echo "Configuration:"
echo "  Concise API: $CONCISE_API_URL"
echo "  OpenAI configured: $([ -n "$OPENAI_API_KEY" ] && echo "Yes" || echo "No (demo mode only)")"
echo ""

echo "Starting demo server on port 3000..."
python app.py

