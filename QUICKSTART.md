# Quick Start Guide

Get up and running with Concise SDK in 5 minutes!

## Option 1: SDK Only (No Database Required)

Perfect for testing and standalone applications.

```bash
# 1. Clone and setup
git clone https://github.com/yourusername/concise.git
cd Concise/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Configure (optional - only needed for TALE zero-shot)
cp ../.env.example ../.env
# Edit .env and add OPENAI_API_KEY if using zero-shot strategy

# 3. Test it works
cd ..
python3 tests/test_comprehensive.py

# 4. Use in your code
python3
>>> from backend.app.hybrid_compressor import HybridCompressor
>>> comp = HybridCompressor()
>>> result = comp.compress('Test prompt', strategy='balanced')
>>> print(f"Compression: {result['compression_ratio']}x")
```

## Option 2: Docker (Easiest)

```bash
# 1. Set environment
cp .env.example .env
# Add your OPENAI_API_KEY

# 2. Start everything
docker-compose up -d

# 3. Test
curl http://localhost:8000/health
```

## First Compression

```python
from backend.app.hybrid_compressor import HybridCompressor

compressor = HybridCompressor()
result = compressor.compress(
    "Your long prompt here...",
    strategy="balanced"  # or "aggressive"
)

print(f"Compression: {result['compression_ratio']}x")
print(f"Tokens: {result['original_tokens']} → {result['compressed_tokens']}")
```

## Next Steps

1. Read [README.md](README.md) for full documentation
2. Run tests: `python3 tests/test_comprehensive.py`
3. Explore `/demo` folder for examples
