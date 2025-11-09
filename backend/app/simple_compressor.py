"""
Simple Aggressive Text Compressor
Achieves 40-60% compression with predictable heuristics
"""
import re
import tiktoken
from typing import Dict

class SimpleCompressor:
    """
    Simple, fast, predictable text compression
    Unlike LLMLingua which is unreliable, this WILL compress text
    """

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Words to remove (articles, fillers, redundancy)
        self.remove_words = {
            'a', 'an', 'the', 'very', 'really', 'quite', 'just', 'actually',
            'basically', 'literally', 'essentially', 'generally', 'typically',
            'usually', 'often', 'sometimes', 'perhaps', 'maybe', 'probably',
            'could', 'would', 'should', 'might', 'may', 'can', 'will', 'shall'
        }

        # Phrase simplifications
        self.simplifications = {
            r'in order to': 'to',
            r'due to the fact that': 'because',
            r'at this point in time': 'now',
            r'for the purpose of': 'to',
            r'in the event that': 'if',
            r'with regard to': 'about',
            r'with reference to': 'about',
            r'it is important to note that': '',
            r'it should be noted that': '',
            r'please note that': '',
            r'as previously mentioned': '',
            r'as stated above': '',
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def compress(self, text: str, target_ratio: float = 0.5) -> Dict:
        """
        Compress text to target ratio

        Args:
            text: Input text
            target_ratio: Target compression (0.5 = keep 50% of tokens, 2x compression)

        Returns:
            Dict with compressed text and stats
        """
        original_text = text
        original_tokens = self.count_tokens(text)

        # Phase 1: Simplify common phrases
        for phrase, replacement in self.simplifications.items():
            text = re.sub(phrase, replacement, text, flags=re.IGNORECASE)

        # Phase 2: Remove filler words (but preserve structure)
        words = text.split()
        filtered_words = []
        for i, word in enumerate(words):
            word_lower = word.lower().strip('.,!?;:')
            # Keep word if:
            # - Not in remove list, OR
            # - First/last word (preserve structure), OR
            # - Followed by punctuation (likely important)
            if (word_lower not in self.remove_words or
                i == 0 or i == len(words) - 1 or
                any(p in word for p in '.,!?;:')):
                filtered_words.append(word)

        text = ' '.join(filtered_words)

        # Phase 3: Remove redundant whitespace
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s([.,!?;:])', r'\1', text)

        # Phase 4: Contract sentences (remove extra conjunctions)
        text = re.sub(r',\s+and\s+', ', ', text)
        text = re.sub(r'\.\s+Also,?\s+', '. ', text)

        compressed_tokens = self.count_tokens(text)
        actual_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0

        # Phase 5: If we haven't hit target, remove more aggressively
        if actual_ratio > target_ratio and compressed_tokens > 10:
            # Remove every nth word until we hit target (brute force)
            words = text.split()
            target_count = int(len(words) * target_ratio)

            if target_count < len(words):
                # Keep first and last, sample middle
                step = max(1, int(len(words) / target_count))
                kept_words = [words[0]]  # Keep first
                kept_words.extend([w for i, w in enumerate(words[1:-1], 1) if i % step == 0])
                kept_words.append(words[-1])  # Keep last
                text = ' '.join(kept_words[:target_count])

        compressed_tokens = self.count_tokens(text)
        tokens_saved = original_tokens - compressed_tokens
        actual_ratio = compressed_tokens / original_tokens if original_tokens > 0 else 1.0
        compression_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0

        return {
            "compressed_text": text.strip(),
            "original_text": original_text,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "compression_ratio": round(compression_ratio, 2),
            "target_ratio": round(1.0 / target_ratio, 2),
            "strategy": "simple_heuristic"
        }


# Test it
if __name__ == "__main__":
    compressor = SimpleCompressor()

    test_text = """You are a helpful customer support agent for TechCorp.

Our product is a cloud-based project management tool that helps teams collaborate on projects. It includes features like task management, file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response."""

    print("SIMPLE COMPRESSOR TEST")
    print("=" * 80)
    print()

    for ratio in [0.7, 0.5, 0.3]:
        result = compressor.compress(test_text, target_ratio=ratio)
        print(f"Target: {result['target_ratio']}x compression")
        print(f"Actual: {result['compression_ratio']}x")
        print(f"Tokens: {result['original_tokens']} → {result['compressed_tokens']}")
        print(f"Compressed: {result['compressed_text'][:150]}...")
        print()
