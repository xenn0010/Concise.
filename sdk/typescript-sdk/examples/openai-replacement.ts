/**
 * OpenAI drop-in replacement example
 */

import { OpenAI } from 'concise-sdk';

const client = new OpenAI({ apiKey: 'your-concise-key' });

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [
    { role: 'system', content: 'You are a helpful Python programming assistant.' },
    { role: 'user', content: 'Write a function to calculate the Fibonacci sequence' }
  ],
  compressionEnabled: true,
  compressionLevel: 'balanced'
});

console.log(response.choices[0].message.content);

if (response.compressionMetadata) {
  const meta = response.compressionMetadata;
  console.log(`\nCompression saved ${meta.tokensSaved} tokens!`);
}
