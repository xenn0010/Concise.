/**
 * Concise API client
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ConciseConfig,
  CompressionResult,
  CompressRequest,
  CompressionLevel,
  HealthResponse,
  EstimationStrategy,
  TALEOptimizeResult,
  TALEValidateResult,
  TALEOptimizeRequest,
  TALEValidateRequest,
} from './types';
import {
  AuthenticationError,
  APIError,
  RateLimitError,
  NetworkError,
} from './exceptions';

/**
 * Official Concise API client
 *
 * Provides direct access to token compression endpoints.
 *
 * @example
 * ```typescript
 * import { Concise } from 'concise-sdk';
 *
 * const client = new Concise({ apiKey: 'your-api-key' });
 *
 * const result = await client.compress('Your long prompt here...', 'auto');
 *
 * console.log(`Saved ${result.tokensSaved} tokens!`);
 * console.log(`Compressed text: ${result.compressedText}`);
 * ```
 */
export class Concise {
  private apiKey: string;
  private baseUrl: string;
  private client: AxiosInstance;

  /**
   * Initialize Concise client
   *
   * @param config - Configuration object
   * @param config.apiKey - Your Concise API key (or set CONCISE_API_KEY env var)
   * @param config.baseUrl - API base URL (default: https://api.concise.dev/v1)
   * @param config.timeout - Request timeout in milliseconds (default: 30000)
   */
  constructor(config: ConciseConfig = {}) {
    this.apiKey = config.apiKey || process.env.CONCISE_API_KEY || '';

    if (!this.apiKey) {
      throw new AuthenticationError(
        'API key required. Pass apiKey in config or set CONCISE_API_KEY environment variable.'
      );
    }

    this.baseUrl = (config.baseUrl || 'https://api.concise.dev/v1').replace(/\/$/, '');

    this.client = axios.create({
      baseURL: this.baseUrl,
      timeout: config.timeout || 30000,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  private setupInterceptors() {
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        if (error.response) {
          const status = error.response.status;
          const data = error.response.data as any;

          if (status === 401) {
            throw new AuthenticationError('Invalid API key');
          } else if (status === 429) {
            throw new RateLimitError('Rate limit exceeded');
          } else if (status >= 400) {
            const message = data?.detail || 'Unknown error';
            throw new APIError(message, status);
          }
        } else if (error.code === 'ECONNABORTED') {
          throw new NetworkError('Request timed out');
        } else {
          throw new NetworkError(`Network error: ${error.message}`);
        }

        throw error;
      }
    );
  }

  /**
   * Compress text to reduce token count
   *
   * @param text - Text to compress (code or natural language)
   * @param level - Compression level
   *   - "auto": Automatic strategy selection (recommended)
   *   - "aggressive": Maximum compression (50% reduction)
   *   - "balanced": Good trade-off (30% reduction)
   *   - "conservative": Light compression (20% reduction)
   *
   * @returns CompressionResult with compressed text and metrics
   *
   * @example
   * ```typescript
   * const result = await client.compress(
   *   'def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)',
   *   'auto'
   * );
   *
   * console.log(`Original: ${result.originalTokens} tokens`);
   * console.log(`Compressed: ${result.compressedTokens} tokens`);
   * console.log(`Saved: ${result.tokensSaved} tokens (${((1-result.compressionRatio)*100).toFixed(1)}%)`);
   * console.log(`Time: ${result.compressionTimeMs.toFixed(0)}ms`);
   * ```
   */
  async compress(text: string, level: CompressionLevel = 'auto'): Promise<CompressionResult> {
    const response = await this.client.post<any>('/compress', {
      text,
      level,
    });

    return {
      originalText: response.data.original_text,
      compressedText: response.data.compressed_text,
      originalTokens: response.data.original_tokens,
      compressedTokens: response.data.compressed_tokens,
      tokensSaved: response.data.tokens_saved,
      compressionRatio: response.data.compression_ratio,
      strategy: response.data.strategy,
      compressionTimeMs: response.data.compression_time_ms,
      cacheHit: response.data.cache_hit,
    };
  }

  /**
   * Optimize prompt to reduce output tokens using TALE
   *
   * TALE (Token-Budget-Aware LLM Reasoning) reduces output tokens by 60-70%
   * by estimating optimal token budgets and constraining LLM generation.
   *
   * @param prompt - The prompt to optimize
   * @param options - Optimization options
   * @param options.strategy - Budget estimation strategy:
   *   - "fixed": Fast heuristic-based estimation (default, 70% confidence)
   *   - "zero_shot": LLM estimates its own budget (85% confidence, 1 extra call)
   *   - "adaptive": Uses user history (85% confidence with history)
   * @param options.targetBudget - Manual token budget override (skips estimation)
   *
   * @returns TALEOptimizeResult with optimized prompt and budget info
   *
   * @example
   * ```typescript
   * // Optimize prompt to reduce output tokens
   * const result = await client.optimizeForOutput('Explain how binary search works', {
   *   strategy: 'fixed'
   * });
   *
   * console.log(`Estimated budget: ${result.estimatedBudget} tokens`);
   * console.log(`Optimized prompt: ${result.optimizedPrompt}`);
   *
   * // Send optimized prompt to LLM
   * const llmResponse = await openai.chat.completions.create({
   *   model: 'gpt-4',
   *   messages: [{ role: 'user', content: result.optimizedPrompt }]
   * });
   *
   * // Expected: 60-70% fewer output tokens!
   * ```
   */
  async optimizeForOutput(
    prompt: string,
    options: { strategy?: EstimationStrategy; targetBudget?: number } = {}
  ): Promise<TALEOptimizeResult> {
    const requestData: TALEOptimizeRequest = {
      prompt,
      strategy: options.strategy || 'fixed',
    };

    if (options.targetBudget !== undefined) {
      requestData.targetBudget = options.targetBudget;
    }

    const response = await this.client.post<any>('/tale/optimize', requestData);

    return {
      optimizedPrompt: response.data.optimized_prompt,
      originalPrompt: response.data.original_prompt,
      estimatedBudget: response.data.estimated_budget,
      budgetMetadata: {
        confidence: response.data.budget_metadata.confidence,
        reasoning: response.data.budget_metadata.reasoning,
        strategy: response.data.budget_metadata.strategy,
        optimizationTimeMs: response.data.budget_metadata.optimization_time_ms,
      },
      promptAdditions: {
        prefix: response.data.prompt_additions.prefix,
        suffix: response.data.prompt_additions.suffix,
      },
    };
  }

  /**
   * Validate that LLM output stayed within token budget
   *
   * Use this after receiving an LLM response to check if the model
   * respected the token budget from optimizeForOutput().
   *
   * @param output - The LLM's generated output
   * @param budget - The token budget (from optimizeForOutput)
   * @param tolerance - Allow budget to exceed by this % (default: 0.2 = 20%)
   *
   * @returns TALEValidateResult with compliance status and metrics
   *
   * @example
   * ```typescript
   * // 1. Optimize prompt
   * const optimized = await client.optimizeForOutput('Explain recursion');
   *
   * // 2. Get LLM response
   * const response = await llm.complete(optimized.optimizedPrompt);
   *
   * // 3. Validate output
   * const validation = await client.validateOutput(response, optimized.estimatedBudget);
   *
   * if (validation.withinBudget) {
   *   console.log(`✅ Saved ${validation.tokensSaved} tokens!`);
   * } else {
   *   console.log(`❌ Exceeded budget by ${validation.exceededBy} tokens`);
   * }
   * ```
   */
  async validateOutput(
    output: string,
    budget: number,
    tolerance: number = 0.2
  ): Promise<TALEValidateResult> {
    const requestData: TALEValidateRequest = {
      output,
      budget,
      tolerance,
    };

    const response = await this.client.post<any>('/tale/validate', requestData);

    return {
      withinBudget: response.data.within_budget,
      actualTokens: response.data.actual_tokens,
      budgetTokens: response.data.budget_tokens,
      maxAllowedTokens: response.data.max_allowed_tokens,
      budgetUtilization: response.data.budget_utilization,
      tokensSaved: response.data.tokens_saved,
      exceededBy: response.data.exceeded_by,
    };
  }

  /**
   * Check API health status
   *
   * @returns Health status and version info
   */
  async health(): Promise<HealthResponse> {
    const response = await this.client.get<HealthResponse>('/health');
    return response.data;
  }
}
