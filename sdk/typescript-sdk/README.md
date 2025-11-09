# Concise TypeScript SDK

Official TypeScript/JavaScript client for [Concise](https://concise.dev) - Token compression for LLMs.

**Full-stack LLM cost optimization platform**

- Input compression: 50% reduction
- Output optimization: 60-70% reduction
- **Combined: 70% total cost savings**

Works with GPT-4, Claude, Gemini, all LLMs.

## Installation

```bash
npm install concise-sdk
# or
yarn add concise-sdk
# or
pnpm add concise-sdk
```

## Quick Start

### Direct Compression API

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

const result = await client.compress(
  'Your long prompt here...',
  'auto'
);

console.log(`Original: ${result.originalTokens} tokens`);
console.log(`Compressed: ${result.compressedTokens} tokens`);
console.log(`Saved: ${result.tokensSaved} tokens (${((1-result.compressionRatio)*100).toFixed(1)}%)`);
console.log(`Compressed text: ${result.compressedText}`);
```

### OpenAI Drop-in Replacement

Replace your OpenAI import with Concise for automatic compression:

```typescript
// Before:
// import OpenAI from 'openai';

// After:
import { OpenAI } from 'concise-sdk';

const client = new OpenAI({ apiKey: 'your-concise-key' });

const response = await client.chat.completions.create({
  model: 'gpt-4',
  messages: [
    { role: 'system', content: 'You are a helpful assistant.' },
    { role: 'user', content: 'Explain quantum computing in simple terms' }
  ],
  compressionEnabled: true,  // Automatic token compression
  compressionLevel: 'balanced'
});

console.log(response.choices[0].message.content);
```

## Features

### Input Optimization (Compression)
- **Direct Compression API** - Compress any text before sending to LLMs
- **OpenAI Drop-in** - Replace OpenAI SDK import with Concise
- **Automatic Strategy Selection** - Detects Python code vs natural language
- **GPU-Accelerated** - 285ms compression time (or instant with caching)
- **Zero Context Loss** - Preserves semantic meaning

### Output Optimization (NEW - TALE)
- **Token Budget Prompting** - Reduce output tokens by 60-70%
- **Budget Estimation** - 3 strategies: fixed, zero_shot, adaptive
- **Output Validation** - Check if LLM stayed within budget
- **LLM-Agnostic** - Works with all models (GPT-4, Claude, Gemini, etc.)
- **Quality Retention** - 95%+ accuracy maintained

### Developer Experience
- **Full TypeScript Support** - Complete type definitions included
- **Error Handling** - Comprehensive exception types

## Compression Levels

| Level | Reduction | Use Case |
|-------|-----------|----------|
| `auto` | 30-50% | Automatic strategy (recommended) |
| `aggressive` | 50% | Maximum compression, natural language |
| `balanced` | 30% | Good trade-off |
| `conservative` | 20% | Light compression, preserve structure |

## Examples

### Full-Stack Optimization (Input + Output)

Combine compression and TALE for maximum savings:

```typescript
import { Concise } from 'concise-sdk';
import OpenAI from 'openai';

const client = new Concise({ apiKey: 'your-api-key' });
const openai = new OpenAI();

const prompt = 'Write a function to implement binary search';

// 1. Compress INPUT tokens (50% reduction)
const compressed = await client.compress(prompt, 'auto');
console.log(`Input: ${compressed.tokensSaved} tokens saved`);

// 2. Optimize for OUTPUT tokens (60-70% reduction)
const optimized = await client.optimizeForOutput(compressed.compressedText, {
  strategy: 'fixed'
});
console.log(`Expected output budget: ${optimized.estimatedBudget} tokens`);

// 3. Send to LLM
const response = await openai.chat.completions.create({
  model: 'gpt-4',
  messages: [{ role: 'user', content: optimized.optimizedPrompt }]
});

// 4. Validate savings
const validation = await client.validateOutput(
  response.choices[0].message.content!,
  optimized.estimatedBudget
);
console.log(`Output: ${validation.tokensSaved} tokens saved`);

// Result: ~70% total cost reduction!
```

### Output Optimization (TALE)

Reduce output tokens by 60-70%:

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

// Optimize prompt to reduce output
const result = await client.optimizeForOutput('Explain how binary search works', {
  strategy: 'fixed'  // or 'zero_shot', 'adaptive'
});

console.log(`Estimated budget: ${result.estimatedBudget} tokens`);
console.log(`Optimized prompt: ${result.optimizedPrompt}`);

// Send to your LLM...
// The LLM will generate 60-70% fewer tokens while maintaining quality
```

**Strategies:**
- `fixed`: Fast heuristic (70% confidence, <10ms)
- `zero_shot`: LLM self-estimation (85% confidence, 1 extra call)
- `adaptive`: User history-based (85% confidence)

### Python Code Compression

```typescript
import { Concise } from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

const code = `
def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
`;

const result = await client.compress(code, 'auto');
// Strategy: token_compression_code
// Reduction: 39%
// Time: 27ms
```

### Natural Language Compression

```typescript
const result = await client.compress(
  'FastAPI is a modern, fast web framework for building APIs with Python 3.8+',
  'aggressive'
);
// Strategy: token_compression_text
// Reduction: 50%
// Time: 285ms (or 0ms if cached)
```

### Using with OpenAI

```typescript
import { OpenAI } from 'concise-sdk';

const client = new OpenAI({ apiKey: 'your-concise-key' });

const response = await client.chat.completions.create({
  model: 'gpt-3.5-turbo',
  messages: [
    {
      role: 'system',
      content: 'You are a Python expert. Help users write clean, efficient code.'
    },
    {
      role: 'user',
      content: 'Write a function to validate email addresses using regex'
    }
  ],
  compressionEnabled: true,
  compressionLevel: 'balanced'
});

console.log(response.choices[0].message.content);
```

### Environment Variable

Set `CONCISE_API_KEY` environment variable:

```bash
export CONCISE_API_KEY=your-api-key
```

```typescript
import { Concise } from 'concise-sdk';

// API key loaded from environment
const client = new Concise();
```

### Next.js Example

```typescript
// app/api/compress/route.ts
import { Concise } from 'concise-sdk';
import { NextResponse } from 'next/server';

const client = new Concise({ apiKey: process.env.CONCISE_API_KEY });

export async function POST(req: Request) {
  const { text } = await req.json();

  const result = await client.compress(text, 'auto');

  return NextResponse.json({
    compressed: result.compressedText,
    tokensSaved: result.tokensSaved
  });
}
```

### Express.js Example

```typescript
import express from 'express';
import { Concise } from 'concise-sdk';

const app = express();
const client = new Concise({ apiKey: process.env.CONCISE_API_KEY });

app.post('/compress', async (req, res) => {
  const { text } = req.body;

  const result = await client.compress(text, 'auto');

  res.json({
    compressed: result.compressedText,
    tokensSaved: result.tokensSaved
  });
});

app.listen(3000);
```

## Error Handling

```typescript
import {
  Concise,
  AuthenticationError,
  APIError,
  RateLimitError,
  NetworkError
} from 'concise-sdk';

const client = new Concise({ apiKey: 'your-api-key' });

try {
  const result = await client.compress('text');
} catch (error) {
  if (error instanceof AuthenticationError) {
    console.error('Invalid API key');
  } else if (error instanceof RateLimitError) {
    console.error('Rate limit exceeded');
  } else if (error instanceof APIError) {
    console.error(`API error: ${error.message} (status: ${error.statusCode})`);
  } else if (error instanceof NetworkError) {
    console.error('Network error');
  }
}
```

## Performance

| Type | Strategy | Reduction | Time |
|------|----------|-----------|------|
| Python code | python-minifier | 39% | 27ms |
| Natural language | LLMLingua-2 GPU | 50% | 285ms |
| Cached requests | Cache hit | 50% | 0ms |

### Caching

Concise automatically caches compression results:
- First request: GPU compression (285ms)
- Repeated requests: Instant (0ms)
- 240,000x speedup for cached requests

## API Reference

### `Concise`

Main client for direct compression API.

#### Constructor

```typescript
new Concise(config?: ConciseConfig)
```

**Parameters:**
- `config.apiKey` (string, optional): Your Concise API key
- `config.baseUrl` (string, optional): API base URL (default: https://api.concise.dev/v1)
- `config.timeout` (number, optional): Request timeout in milliseconds (default: 30000)

#### Methods

##### `compress(text, level)`

Compress text to reduce token count.

```typescript
async compress(text: string, level?: CompressionLevel): Promise<CompressionResult>
```

**Parameters:**
- `text` (string): Text to compress
- `level` (string): Compression level ("auto", "aggressive", "balanced", "conservative")

**Returns:**
- `Promise<CompressionResult>`: Object with compression metrics

##### `optimizeForOutput(prompt, options)`

Optimize prompt to reduce output tokens using TALE.

```typescript
async optimizeForOutput(
  prompt: string,
  options?: { strategy?: EstimationStrategy; targetBudget?: number }
): Promise<TALEOptimizeResult>
```

**Parameters:**
- `prompt` (string): Prompt to optimize
- `options.strategy` (string): Estimation strategy ("fixed", "zero_shot", "adaptive")
- `options.targetBudget` (number): Manual token budget override

**Returns:**
- `Promise<TALEOptimizeResult>`: Optimized prompt and budget info

##### `validateOutput(output, budget, tolerance)`

Validate that LLM output stayed within token budget.

```typescript
async validateOutput(
  output: string,
  budget: number,
  tolerance?: number
): Promise<TALEValidateResult>
```

**Parameters:**
- `output` (string): LLM's generated output
- `budget` (number): Token budget from optimizeForOutput
- `tolerance` (number): Allow budget to exceed by this % (default: 0.2)

**Returns:**
- `Promise<TALEValidateResult>`: Compliance status and metrics

##### `health()`

Check API health status.

```typescript
async health(): Promise<HealthResponse>
```

**Returns:**
- `Promise<HealthResponse>`: Status and version info

### `OpenAI`

OpenAI-compatible client with automatic compression.

#### Constructor

```typescript
new OpenAI(config?: ConciseConfig)
```

#### Methods

##### `chat.completions.create(request)`

Create chat completion with compression.

```typescript
async create(request: ChatCompletionRequest): Promise<ChatCompletionResponse>
```

**Additional Parameters:**
- `compressionEnabled` (boolean): Enable compression (default: true)
- `compressionLevel` (string): Compression level (default: "auto")

## Types

### `CompressionResult`

```typescript
interface CompressionResult {
  originalText: string;
  compressedText: string;
  originalTokens: number;
  compressedTokens: number;
  tokensSaved: number;
  compressionRatio: number;
  strategy: string;
  compressionTimeMs: number;
  cacheHit?: boolean;
}
```

### `ChatCompletionRequest`

```typescript
interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  compressionEnabled?: boolean;
  compressionLevel?: CompressionLevel;
}
```

### `TALEOptimizeResult`

```typescript
interface TALEOptimizeResult {
  optimizedPrompt: string;
  originalPrompt: string;
  estimatedBudget: number;
  budgetMetadata: {
    confidence: number;
    reasoning: string;
    strategy: EstimationStrategy;
    optimizationTimeMs: number;
  };
  promptAdditions: {
    prefix: string;
    suffix: string;
  };
}
```

### `TALEValidateResult`

```typescript
interface TALEValidateResult {
  withinBudget: boolean;
  actualTokens: number;
  budgetTokens: number;
  maxAllowedTokens: number;
  budgetUtilization: number;
  tokensSaved: number;
  exceededBy: number;
}
```

## Requirements

- Node.js 16+
- TypeScript 5.0+ (for TypeScript projects)

## Getting Your API Key

1. Sign up at [concise.dev](https://concise.dev)
2. Create an API key in the dashboard
3. Use the key with this SDK

## Support

- Documentation: [docs.concise.dev](https://docs.concise.dev)
- Issues: [github.com/concise/typescript-sdk/issues](https://github.com/concise/typescript-sdk/issues)
- Email: support@concise.dev

## License

MIT License - see LICENSE file for details
