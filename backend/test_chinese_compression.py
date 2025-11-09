"""
Test: Chinese token compression hypothesis
Chinese text uses fewer tokens than English for same meaning
"""
import tiktoken
from deep_translator import GoogleTranslator

tokenizer = tiktoken.encoding_for_model("gpt-3.5-turbo")

# Test cases
test_texts = [
    """
    You are an expert software engineering assistant with comprehensive knowledge of modern
    development practices, programming languages, frameworks, and system architecture. Your
    primary role is to help developers solve complex technical challenges, debug issues,
    design scalable systems, and write production-quality code.
    """,
    """
    FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+
    based on standard Python type hints. It is one of the fastest Python frameworks available,
    on par with NodeJS and Go, thanks to Starlette for the web parts and Pydantic for the data parts.
    """,
]

print("="*70)
print("CHINESE TOKEN COMPRESSION TEST")
print("="*70)

try:
    translator_to_cn = GoogleTranslator(source='en', target='zh-CN')
    translator_to_en = GoogleTranslator(source='zh-CN', target='en')

    total_en_tokens = 0
    total_cn_tokens = 0

    for i, text in enumerate(test_texts, 1):
        text = text.strip()

        # English tokens
        en_tokens = len(tokenizer.encode(text))

        # Translate to Chinese
        chinese_text = translator_to_cn.translate(text)

        # Chinese tokens
        cn_tokens = len(tokenizer.encode(chinese_text))

        # Translate back to English
        back_to_en = translator_to_en.translate(chinese_text)
        back_tokens = len(tokenizer.encode(back_to_en))

        reduction = (1 - cn_tokens/en_tokens) * 100

        print(f"\nTest {i}:")
        print(f"  Original English: {en_tokens} tokens")
        print(f"    {text[:100]}...")
        print(f"  Chinese: {cn_tokens} tokens ({reduction:+.1f}%)")
        print(f"    {chinese_text[:100]}...")
        print(f"  Back to English: {back_tokens} tokens")
        print(f"    {back_to_en[:100]}...")

        total_en_tokens += en_tokens
        total_cn_tokens += cn_tokens

    overall_reduction = (1 - total_cn_tokens/total_en_tokens) * 100

    print("\n" + "="*70)
    print("RESULTS")
    print("="*70)
    print(f"Total English tokens: {total_en_tokens}")
    print(f"Total Chinese tokens: {total_cn_tokens}")
    print(f"Overall compression: {overall_reduction:.1f}%")

    print("\n" + "="*70)
    print("ANALYSIS")
    print("="*70)

    if overall_reduction > 0:
        print(f"✓ Chinese IS more token-efficient ({overall_reduction:.0f}% reduction)")
        print(f"\nPros:")
        print(f"  - Automatic {overall_reduction:.0f}% token reduction")
        print(f"  - No ML model needed (just translation API)")
        print(f"  - Fast (translation ~100-200ms)")
        print(f"\nCons:")
        print(f"  - Meaning loss in translation")
        print(f"  - Back-translation may change semantics")
        print(f"  - Adds 200-400ms latency (2x translation)")
        print(f"  - Translation API costs money")
        print(f"  - LLM still needs to understand Chinese")
    else:
        print(f"✗ Chinese is NOT more efficient ({overall_reduction:.1f}% INCREASE)")

except Exception as e:
    print(f"\nNote: Need to install deep-translator")
    print(f"Run: pip install deep-translator")
    print(f"\nManual test instead:")

    # Manual test without translation
    text_en = "You are an expert software engineering assistant"
    text_cn = "您是一位专业的软件工程助手"

    en_tokens = len(tokenizer.encode(text_en))
    cn_tokens = len(tokenizer.encode(text_cn))

    print(f"\nEnglish: \"{text_en}\"")
    print(f"  Tokens: {en_tokens}")
    print(f"\nChinese: \"{text_cn}\"")
    print(f"  Tokens: {cn_tokens}")
    print(f"\nReduction: {(1 - cn_tokens/en_tokens)*100:.1f}%")

    if cn_tokens < en_tokens:
        print("\n✓ Chinese uses fewer tokens for same meaning")
    else:
        print("\n✗ Chinese does NOT save tokens")

print("\n" + "="*70)
print("CONCLUSION FOR VIBECON")
print("="*70)
print("\nThis approach is clever BUT:")
print("1. Translation adds latency (200-400ms)")
print("2. Translation API costs money (defeats purpose)")
print("3. Meaning loss in translation")
print("4. Most LLMs already handle Chinese well")
print("5. Users want English prompts to stay English")
print("\nVerdict: Interesting hack, but not production-ready for VibeCon")
print("="*70)
