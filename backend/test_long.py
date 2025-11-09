#!/usr/bin/env python3
import sys
sys.path.insert(0, '/home/yab/Concise/backend')
from app.compressor import get_compressor

# Longer test text
text = """
I am working on a project that requires user authentication. I need to understand
how to implement a secure login system using JWT tokens. Can you please explain to me
step by step how to create the authentication middleware, how to generate tokens, how
to validate them, and how to handle token expiration? I would really appreciate a
detailed explanation with code examples if possible. Thank you so much for your help!

The authentication system in our application is built using JSON Web Tokens (JWT).
When a user logs in, the server validates their credentials against the database.
If the credentials are correct, the server generates a JWT token that contains the
user's ID, email, and role. This token is signed using a secret key stored in the
environment variables. The token has an expiration time of 24 hours. When the user
makes subsequent requests, they include this token in the Authorization header of
the HTTP request. The server then validates the token by verifying the signature
using the same secret key. If the token is valid and not expired, the server extracts
the user information from the token and proceeds with the request.
""" * 3  # Repeat 3 times to make it longer

compressor = get_compressor()
result = compressor.compress(text, strategy="balanced", use_cache=False)

print(f"\n✅ Compression successful!")
print(f"   Original: {result['original_tokens']} tokens")
print(f"   Compressed: {result['compressed_tokens']} tokens")
print(f"   Saved: {result['tokens_saved']} tokens")
print(f"   Ratio: {result['compression_ratio']}x")
print(f"   Cost saved: ${result['cost_saved_usd']}")
print(f"   Time: {result['compression_time_ms']}ms")
print(f"\n📝 Compressed text preview:")
print(f"   {result['compressed_text'][:200]}...")
