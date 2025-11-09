"""
OpenAI drop-in replacement example
"""

from concise import OpenAI

client = OpenAI(api_key="your-concise-key")

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": "You are a helpful Python programming assistant."},
        {"role": "user", "content": "Write a function to calculate the Fibonacci sequence"}
    ],
    compression_enabled=True,
    compression_level="balanced"
)

print(response["choices"][0]["message"]["content"])

if response.get("compression_metadata"):
    meta = response["compression_metadata"]
    print(f"\n Compression saved {meta['tokens_saved']} tokens!")
