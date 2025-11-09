"""
Smart Semantic Compressor
Compresses text while PRESERVING meaning and readability for LLMs

Strategy: LLMs understand context well, so we can:
1. Remove redundancy (repeated concepts)
2. Use shorter synonyms
3. Simplify structure
4. Keep key nouns/verbs/entities
5. Maintain grammatical coherence
"""
import re
import tiktoken
from typing import Dict, List, Set

class SmartCompressor:
    """
    Semantic-preserving compression that LLMs can understand
    """

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base")

        # Safe-to-remove filler words (doesn't hurt meaning)
        self.safe_fillers = {
            'actually', 'basically', 'literally', 'essentially',
            'generally', 'typically', 'usually', 'really', 'very',
            'quite', 'rather', 'somewhat', 'extremely', 'incredibly'
        }

        # Redundant phrases that can be shortened
        self.phrase_replacements = {
            # Verbose → Concise (but still grammatical)
            r'\bin order to\b': 'to',
            r'\bdue to the fact that\b': 'because',
            r'\bat this point in time\b': 'now',
            r'\bfor the purpose of\b': 'to',
            r'\bin the event that\b': 'if',
            r'\bwith regard to\b': 'regarding',
            r'\bwith reference to\b': 'regarding',
            r'\bas a matter of fact\b': '',
            r'\bit is important to note that\b': '',
            r'\bit should be noted that\b': '',
            r'\bplease note that\b': '',
            r'\bas previously mentioned\b': '',
            r'\bas mentioned earlier\b': '',
            r'\bas stated above\b': '',
            r'\bthe fact that\b': 'that',
            r'\buntil such time as\b': 'until',
            r'\bin spite of the fact that\b': 'although',
            r'\bby means of\b': 'by',
            r'\bfor the reason that\b': 'because',
        }

        # Short synonyms for common long words (preserve meaning)
        self.word_replacements = {
            'assistance': 'help',
            'utilize': 'use',
            'implement': 'use',
            'demonstrate': 'show',
            'additional': 'more',
            'numerous': 'many',
            'frequently': 'often',
            'immediately': 'now',
            'approximately': 'about',
            'subsequently': 'later',
            'previously': 'before',
            'sufficient': 'enough',
            'require': 'need',
            'purchase': 'buy',
            'terminate': 'end',
            'commence': 'start',
            'acquire': 'get',
            'modify': 'change',
            'endeavor': 'try',
            'facilitate': 'help',
        }

    def count_tokens(self, text: str) -> int:
        """Count tokens"""
        return len(self.tokenizer.encode(text))

    def remove_redundancy(self, text: str) -> str:
        """
        Remove redundant sentences/phrases
        LLMs are good at inferring from context
        """
        # Remove repetitive explanations
        lines = text.split('\n')
        seen_concepts = set()
        unique_lines = []

        for line in lines:
            # Extract key concepts (simple word-based check)
            words = set(re.findall(r'\w+', line.lower()))

            # Check if this line adds new information
            new_info = words - seen_concepts

            # Keep if it adds significant new information OR is very short (likely important)
            if len(new_info) > 3 or len(line) < 30:
                unique_lines.append(line)
                seen_concepts.update(words)

        return '\n'.join(unique_lines)

    def simplify_structure(self, text: str) -> str:
        """
        Simplify sentence structure while keeping meaning
        """
        # Remove politeness padding (LLMs understand direct instructions)
        text = re.sub(r'^(Please |Kindly |Could you please |Would you mind )', '', text, flags=re.MULTILINE)

        # Simplify question forms
        text = re.sub(r'Can you (please )?(help me )?(to )?', '', text, flags=re.IGNORECASE)
        text = re.sub(r'I would like (you )?to ', '', text, flags=re.IGNORECASE)
        text = re.sub(r"I'd like to ", '', text, flags=re.IGNORECASE)

        # Remove meta-commentary
        text = re.sub(r'Let me (explain|describe|tell you about) ', '', text, flags=re.IGNORECASE)

        return text

    def compress_balanced(self, text: str) -> str:
        """
        Balanced compression: ~30-40% reduction, high readability
        """
        # Phase 1: Remove redundancy
        text = self.remove_redundancy(text)

        # Phase 2: Simplify phrases
        for pattern, replacement in self.phrase_replacements.items():
            text = re.sub(pattern, replacement, text, flags=re.IGNORECASE)

        # Phase 3: Remove safe fillers
        words = text.split()
        filtered = [w for w in words if w.lower().strip('.,!?;:') not in self.safe_fillers]
        text = ' '.join(filtered)

        # Phase 4: Simplify structure
        text = self.simplify_structure(text)

        # Phase 5: Clean whitespace
        text = re.sub(r'\n\s*\n\s*\n+', '\n\n', text)  # Max 1 blank line
        text = re.sub(r' +', ' ', text)  # Single spaces
        text = text.strip()

        return text

    def compress_aggressive(self, text: str) -> str:
        """
        Aggressive compression: ~50-60% reduction, still understandable
        Uses list/bullet format which LLMs parse well
        """
        # Start with balanced compression
        text = self.compress_balanced(text)

        # Replace long words with shorter synonyms
        words = text.split()
        simplified = []
        for word in words:
            word_clean = word.lower().strip('.,!?;:')
            if word_clean in self.word_replacements:
                # Preserve original capitalization/punctuation
                replacement = self.word_replacements[word_clean]
                if word[0].isupper():
                    replacement = replacement.capitalize()
                # Add back punctuation
                for char in '.,!?;:':
                    if char in word:
                        replacement += char
                simplified.append(replacement)
            else:
                simplified.append(word)
        text = ' '.join(simplified)

        # Convert to more compact list format if appropriate
        if '\n-' in text or '\n*' in text:
            # Already has lists, keep them
            pass

        # Remove articles in lists only (preserve in sentences)
        lines = text.split('\n')
        compressed_lines = []
        for line in lines:
            if line.strip().startswith(('-', '*', '•')):
                # Remove articles from list items
                line = re.sub(r'\b(a|an|the)\s+', '', line, flags=re.IGNORECASE)
            compressed_lines.append(line)
        text = '\n'.join(compressed_lines)

        return text

    def compress(
        self,
        text: str,
        strategy: str = "balanced",
        target_ratio: float = None
    ) -> Dict:
        """
        Compress text with semantic preservation

        Args:
            text: Input text
            strategy: "balanced" (30-40% reduction) or "aggressive" (50-60% reduction)
            target_ratio: Override with specific ratio (e.g., 0.5 = keep 50%)

        Returns:
            Compression results
        """
        original_text = text
        original_tokens = self.count_tokens(text)

        # Apply compression
        if strategy == "aggressive" or (target_ratio and target_ratio <= 0.5):
            compressed_text = self.compress_aggressive(text)
        else:
            compressed_text = self.compress_balanced(text)

        compressed_tokens = self.count_tokens(compressed_text)
        tokens_saved = original_tokens - compressed_tokens
        compression_ratio = original_tokens / compressed_tokens if compressed_tokens > 0 else 1.0

        return {
            "compressed_text": compressed_text,
            "original_text": original_text,
            "original_tokens": original_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": tokens_saved,
            "compression_ratio": round(compression_ratio, 2),
            "strategy": strategy
        }


# Test
if __name__ == "__main__":
    compressor = SmartCompressor()

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

    print("SMART SEMANTIC COMPRESSOR TEST")
    print("=" * 80)
    print()

    print(f"Original ({compressor.count_tokens(test_text)} tokens):")
    print(test_text)
    print()
    print("=" * 80)
    print()

    # Test balanced
    print("BALANCED COMPRESSION (readable, ~35% reduction):")
    result = compressor.compress(test_text, strategy="balanced")
    print(f"Tokens: {result['original_tokens']} → {result['compressed_tokens']} ({result['compression_ratio']}x)")
    print()
    print(result['compressed_text'])
    print()
    print("=" * 80)
    print()

    # Test aggressive
    print("AGGRESSIVE COMPRESSION (compact, ~55% reduction):")
    result = compressor.compress(test_text, strategy="aggressive")
    print(f"Tokens: {result['original_tokens']} → {result['compressed_tokens']} ({result['compression_ratio']}x)")
    print()
    print(result['compressed_text'])
    print()
    print("=" * 80)
    print()

    print("KEY DIFFERENCE FROM SIMPLE COMPRESSOR:")
    print("- Maintains grammatical structure")
    print("- Preserves key entities and concepts")
    print("- LLMs can still understand the context")
    print("- Less aggressive but more reliable")
