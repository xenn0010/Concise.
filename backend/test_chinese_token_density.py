"""
Quick test: Do Chinese characters save tokens?
"""
import tiktoken

tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Same meaning in English vs Chinese
pairs = [
    ("You are an expert software engineering assistant",
     "您是一位专业的软件工程助手"),

    ("Hello, how are you today?",
     "你好，你今天怎么样？"),

    ("The quick brown fox jumps over the lazy dog",
     "敏捷的棕色狐狸跳过懒狗"),

    ("Please help me debug this Python code",
     "请帮我调试这段Python代码"),

    ("FastAPI is a modern web framework for building APIs",
     "FastAPI是一个用于构建API的现代Web框架"),
]

print("="*70)
print("CHINESE vs ENGLISH TOKEN DENSITY")
print("="*70)

total_en = 0
total_cn = 0

for en, cn in pairs:
    en_tokens = len(tokenizer.encode(en))
    cn_tokens = len(tokenizer.encode(cn))

    total_en += en_tokens
    total_cn += cn_tokens

    reduction = (1 - cn_tokens/en_tokens) * 100

    print(f"\nEnglish: \"{en}\"")
    print(f"  Tokens: {en_tokens}")
    print(f"Chinese: \"{cn}\"")
    print(f"  Tokens: {cn_tokens}")
    print(f"  Change: {reduction:+.1f}%")

overall = (1 - total_cn/total_en) * 100

print("\n" + "="*70)
print(f"TOTAL: English {total_en} tokens → Chinese {total_cn} tokens")
print(f"Overall: {overall:+.1f}%")
print("="*70)

if overall > 0:
    print(f"\n✓ Chinese saves {overall:.0f}% tokens!")
    print("\nBUT... problems:")
    print("  1. Translation API costs (Google Translate, DeepL)")
    print("  2. Translation latency (~100-200ms each way = 200-400ms total)")
    print("  3. Meaning loss/distortion")
    print("  4. LLM output is in Chinese - need to translate back")
    print("  5. Users expect English in/out")
    print("\nVerdict: Clever but not practical")
else:
    print(f"\n✗ Chinese actually uses MORE tokens ({abs(overall):.0f}% more)")

print("\n" + "="*70)
print("BETTER APPROACH: LLMLingua-2")
print("="*70)
print("  - 20-35% compression")
print("  - Preserves English")
print("  - No translation needed")
print("  - GPU: ~100ms latency")
print("="*70)
