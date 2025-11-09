"""
Hybrid Compressor: Best of Both Worlds
- Uses smart semantic compression first (preserve meaning)
- Then applies selective aggressive compression if needed
- Validates output quality before returning
"""
import re
import tiktoken
from typing import Dict, List, Set
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from smart_compressor import SmartCompressor

class HybridCompressor:
    """
    Intelligent compression that balances reduction vs readability

    Approach:
    1. Smart semantic compression (safe, grammatical)
    2. Selective word removal (target important vs filler)
    3. Quality validation (ensure LLM can understand)
    """

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.smart = SmartCompressor()

        # Words that are SAFE to remove (low semantic value)
        self.removable_words = {
            # Articles
            'a', 'an', 'the',
            # Weak intensifiers
            'very', 'really', 'quite', 'rather', 'pretty', 'fairly',
            # Hedging
            'perhaps', 'maybe', 'possibly', 'probably',
            # Redundant conjunctions (in some contexts)
            'also', 'additionally', 'furthermore',
            # Weak modals (context-dependent)
            'might', 'could', 'would', 'should'
        }

        # Words to NEVER remove (high semantic value)
        self.protected_words = {
            # Question words
            'what', 'when', 'where', 'who', 'why', 'how', 'which',
            # Negation
            'not', 'no', 'never', 'none', 'neither', 'nor',
            # Core verbs
            'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'do', 'does', 'did', 'done', 'doing',
            'have', 'has', 'had',
            # Important prepositions
            'of', 'in', 'on', 'at', 'to', 'for', 'with', 'from',
            # Numbers and entities
            # (handled by regex)
        }

    def count_tokens(self, text: str) -> int:
        return len(self.tokenizer.encode(text))

    def is_protected(self, word: str, position: str = "middle") -> bool:
        """
        Check if a word should be protected from removal

        Args:
            word: The word to check
            position: "start", "middle", or "end" of sentence
        """
        word_lower = word.lower().strip('.,!?;:')

        # Always protect
        if word_lower in self.protected_words:
            return True

        # Protect numbers
        if re.match(r'^\d', word):
            return True

        # Protect capitalized words (likely entities)
        if word[0].isupper() and position != "start":
            return True

        # Protect first and last words of sentences
        if position in ("start", "end"):
            return True

        return False

    def selective_word_removal(self, text: str, target_ratio: float) -> str:
        """
        Remove words selectively to hit target ratio
        Prioritizes removing low-value words while keeping meaning
        """
        sentences = re.split(r'([.!?]\s+)', text)
        compressed_sentences = []

        for i in range(0, len(sentences), 2):
            if i >= len(sentences):
                break

            sentence = sentences[i]
            delimiter = sentences[i+1] if i+1 < len(sentences) else ""

            words = sentence.split()
            if len(words) <= 3:  # Don't compress very short sentences
                compressed_sentences.append(sentence + delimiter)
                continue

            # Score each word by removability
            word_scores = []
            for j, word in enumerate(words):
                position = "start" if j == 0 else ("end" if j == len(words)-1 else "middle")
                word_clean = word.lower().strip('.,!?;:')

                if self.is_protected(word, position):
                    score = 1000  # Never remove
                elif word_clean in self.removable_words:
                    score = 1  # Remove first
                else:
                    score = 10  # Remove if necessary

                word_scores.append((word, score))

            # Calculate how many words to keep
            current_tokens = self.count_tokens(sentence)
            target_tokens = int(current_tokens * target_ratio)

            # Sort by score (low score = remove first)
            sorted_words = sorted(word_scores, key=lambda x: x[1])

            # Keep words until we hit target
            kept_words = []
            for word, score in sorted_words:
                if score >= 1000:  # Protected
                    kept_words.append(word)
                elif len(' '.join(kept_words)) < target_tokens * 4:  # Rough char estimate
                    kept_words.append(word)

            # Preserve original order
            final_words = [w for w, _ in word_scores if w in kept_words]

            compressed_sentences.append(' '.join(final_words) + delimiter)

        return ''.join(compressed_sentences)

    def compress(
        self,
        text: str,
        strategy: str = "balanced",
        target_ratio: float = None
    ) -> Dict:
        """
        Hybrid compression with quality preservation

        Args:
            text: Input text
            strategy: "balanced" (~1.5x, very readable) or "aggressive" (~2-3x, compact but clear)
            target_ratio: Manual override (0.5 = keep 50%, 0.33 = keep 33%)
        """
        original_text = text
        original_tokens = self.count_tokens(text)

        # Step 1: Always start with smart semantic compression (safe)
        compressed = self.smart.compress_balanced(text)
        intermediate_tokens = self.count_tokens(compressed)

        # Safety check: If compression removed everything, fall back to original
        if not compressed or intermediate_tokens == 0:
            compressed = text
            intermediate_tokens = original_tokens

        # Step 2: If we need more compression, apply selective removal
        if strategy == "aggressive" or (target_ratio and target_ratio < 0.7):
            # Set target
            if target_ratio:
                final_target = target_ratio
            else:
                final_target = 0.4  # 2.5x compression for aggressive

            # Calculate remaining compression needed
            current_ratio = intermediate_tokens / original_tokens
            if current_ratio > final_target:
                # Need more compression
                adjusted_target = final_target / current_ratio
                compressed = self.selective_word_removal(compressed, adjusted_target)

        compressed_tokens = self.count_tokens(compressed)

        # Final safety: If we compressed to nothing, return original
        if compressed_tokens == 0 or not compressed.strip():
            compressed = original_text
            compressed_tokens = original_tokens
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0

        # Step 3: Quality validation
        quality = self._assess_quality(original_text, compressed)

        return {
            "compressed_text": compressed,
            "original_text": original_text,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "compression_ratio": round(compression_ratio, 2),
            "strategy": strategy,
            "quality_score": quality
        }

    def _assess_quality(self, original: str, compressed: str) -> float:
        """
        Assess if compressed text maintains meaning
        Simple heuristic: check if key entities/concepts are preserved
        """
        # Extract important words (capitalized, numbers, long words)
        def extract_key_terms(text):
            words = re.findall(r'\b\w+\b', text)
            key_terms = set()
            for word in words:
                if (len(word) > 6 or  # Long words
                    word[0].isupper() or  # Capitalized
                    re.match(r'^\d', word)):  # Numbers
                    key_terms.add(word.lower())
            return key_terms

        original_terms = extract_key_terms(original)
        compressed_terms = extract_key_terms(compressed)

        if len(original_terms) == 0:
            return 1.0

        # What % of key terms were preserved?
        preserved = len(original_terms & compressed_terms)
        quality = preserved / len(original_terms)

        return round(quality, 2)


# Test
if __name__ == "__main__":
    compressor = HybridCompressor()

    test_cases = [
        {
            "name": "Customer Support",
            "text": """You are a helpful customer support agent for TechCorp.

Our product is a cloud-based project management tool that helps teams collaborate on projects. It includes features like task management, file sharing, real-time chat, and analytics dashboards.

Common issues include:
- Login problems
- File upload errors
- Notification settings
- Billing questions
- Integration with third-party tools

Customer question: How do I reset my password?

Please provide a helpful, detailed response."""
        },
        {
            "name": "Code Documentation",
            "text": """Generate comprehensive documentation for this function:

Function name: calculate_total_price
Code:
def calculate_total_price(items, tax_rate=0.08, discount_code=None):
    subtotal = sum(item['price'] * item['quantity'] for item in items)
    if discount_code == 'SAVE10':
        subtotal *= 0.9
    elif discount_code == 'SAVE20':
        subtotal *= 0.8
    tax = subtotal * tax_rate
    return subtotal + tax

Include:
- Purpose and description
- Parameters with types
- Return value
- Exceptions raised
- Usage example"""
        }
    ]

    for test in test_cases:
        print(f"\n{'='*80}")
        print(f"TEST: {test['name']}")
        print('='*80)
        print()

        original_tokens = compressor.count_tokens(test['text'])
        print(f"Original: {original_tokens} tokens")
        print(test['text'][:200] + "...")
        print()

        # Balanced
        result = compressor.compress(test['text'], strategy="balanced")
        print(f"BALANCED: {result['compression_ratio']}x compression, quality={result['quality_score']}")
        print(result['compressed_text'][:200] + "...")
        print()

        # Aggressive
        result = compressor.compress(test['text'], strategy="aggressive")
        print(f"AGGRESSIVE: {result['compression_ratio']}x compression, quality={result['quality_score']}")
        print(result['compressed_text'][:200] + "...")
        print()
