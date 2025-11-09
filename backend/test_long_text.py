#!/usr/bin/env python3
from llmlingua import PromptCompressor
import json

compressor = PromptCompressor(model_name="gpt2", device_map="cpu")

# The text that failed before
long_text = """
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
""" * 3

print(f"Text length: {len(long_text)} chars")
print(f"Estimated tokens: ~{len(long_text.split())} words")

try:
    print("\nCompressing with rate=0.2 (target 5x compression)...")
    result = compressor.compress_prompt(long_text, rate=0.2)

    print(f"✅ Success!")
    print(f"   Original tokens: {result['origin_tokens']}")
    print(f"   Compressed tokens: {result['compressed_tokens']}")
    print(f"   Ratio: {result['ratio']}")
    print(f"   Rate: {result['rate']}")
    print(f"   Compressed preview: {result['compressed_prompt'][:200]}...")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
