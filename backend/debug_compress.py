#!/usr/bin/env python3
"""
Debug script to test compression directly
"""

import sys
sys.path.insert(0, '/home/yab/Concise/backend')

from app.compressor import get_compressor

# Test text
text = """Please help me understand how to implement authentication in my application.
I need to know about JWT tokens, how they work, how to validate them, and how to handle
token expiration. I would really appreciate a detailed explanation with code examples
if possible. Thank you so much for your help!"""

print("Creating compressor...")
compressor = get_compressor()

print("Compressing text...")
try:
    result = compressor.compress(text, strategy="balanced", use_cache=False)
    print("Success!")
    print(f"Compression result: {result}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
