#!/bin/bash
# Local Deployment Script (No Docker Required)

echo "🚀 Deploying Concise SDK Locally..."
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi

echo "✅ Python found: $(python3 --version)"

# Setup backend
cd "$(dirname "$0")/backend"

# Create venv if not exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate and install
echo "📦 Installing dependencies..."
source venv/bin/activate
pip install -q -r requirements.txt

# Check for .env
if [ ! -f "../.env" ]; then
    echo "⚠️  No .env file found. Copying from .env.example..."
    cp ../.env.example ../.env
    echo "📝 Please edit .env and add your OPENAI_API_KEY (optional)"
fi

echo ""
echo "✅ Deployment complete!"
echo ""
echo "📊 Running quick test..."
cd ..
python3 -c "
from backend.app.hybrid_compressor import HybridCompressor
comp = HybridCompressor()
result = comp.compress('This is a test prompt to verify compression works correctly.', strategy='balanced')
print(f'✅ Compression working: {result[\"compression_ratio\"]}x ratio')
print(f'   Tokens: {result[\"original_tokens\"]} → {result[\"compressed_tokens\"]}')
"

echo ""
echo "🎉 Concise SDK is ready to use!"
echo ""
echo "Next steps:"
echo "  1. Edit .env file (add OPENAI_API_KEY if using TALE zero-shot)"
echo "  2. Run tests: python3 tests/test_comprehensive.py"
echo "  3. Start API: cd backend && source venv/bin/activate && uvicorn app.main:app"
echo ""
