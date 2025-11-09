/**
 * Basic compression example
 */

import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

const text = 'FastAPI is a modern, fast web framework for building APIs with Python 3.8+';

const result = await client.compress(text, 'auto');

console.log(`Original: ${result.originalTokens} tokens`);
console.log(`Compressed: ${result.compressedTokens} tokens`);
console.log(`Saved: ${result.tokensSaved} tokens (${((1-result.compressionRatio)*100).toFixed(1)}%)`);
console.log(`Time: ${result.compressionTimeMs.toFixed(0)}ms`);
console.log(`\nOriginal text:\n${result.originalText}`);
console.log(`\nCompressed text:\n${result.compressedText}`);
