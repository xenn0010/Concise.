/**
 * OpenAI-compatible wrapper with automatic compression
 *
 * Drop-in replacement for the OpenAI SDK
 */

import axios, { AxiosInstance, AxiosError } from 'axios';
import {
  ConciseConfig,
  ChatCompletionRequest,
  ChatCompletionResponse,
  CompressionLevel,
} from './types';
import {
  AuthenticationError,
  APIError,
  RateLimitError,
  NetworkError,
} from './exceptions';

class ChatCompletions {
  constructor(private client: OpenAI) {}

  /**
   * Create a chat completion with automatic compression
   *
   * This is a drop-in replacement for the OpenAI SDK's chat completions endpoint
   * with automatic token compression.
   *
   * @param request - Chat completion request
   * @returns Chat completion response
   *
   * @example
   * ```typescript
   * const response = await client.chat.completions.create({
   *   model: 'gpt-4',
   *   messages: [
   *     { role: 'system', content: 'You are a helpful assistant.' },
   *     { role: 'user', content: 'Explain quantum computing' }
   *   ],
   *   compressionEnabled: true,
   *   compressionLevel: 'balanced'
   * });
   *
   * console.log(response.choices[0].message.content);
   * ```
   */
  async create(request: ChatCompletionRequest): Promise<ChatCompletionResponse> {
    return this.client.makeRequest('POST', '/chat/completions', request);
  }
}

class Chat {
  public completions: ChatCompletions;

  constructor(client: OpenAI) {
    this.completions = new ChatCompletions(client);
  }
}

/**
 * OpenAI-compatible client with automatic compression
 *
 * Drop-in replacement for the OpenAI SDK that automatically
 * compresses prompts to save tokens and reduce costs.
 *
 * @example
 * ```typescript
 * // Instead of:
 * // import OpenAI from 'openai';
 * // const client = new OpenAI({ apiKey: 'sk-...' });
 *
 * // Use:
 * import { OpenAI } from 'concise-sdk';
 * const client = new OpenAI({ apiKey: 'your-concise-key' });
 *
 * // Everything else works the same!
 * const response = await client.chat.completions.create({
 *   model: 'gpt-4',
 *   messages: [{ role: 'user', content: 'Hello!' }]
 * });
 * ```
 */
export class OpenAI {
  private apiKey: string;
  private baseUrl: string;
  private client: AxiosInstance;
  public chat: Chat;

  /**
   * Initialize OpenAI-compatible client
   *
   * @param config - Configuration object
   * @param config.apiKey - Your Concise API key (or set CONCISE_API_KEY env var)
   * @param config.baseUrl - API base URL (default: https://api.concise.dev/v1)
   * @param config.timeout - Request timeout in milliseconds (default: 60000)
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
      timeout: config.timeout || 60000,
      headers: {
        'X-API-Key': this.apiKey,
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
    this.chat = new Chat(this);
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

  async makeRequest(method: string, endpoint: string, data?: any): Promise<any> {
    const response = await this.client.request({
      method,
      url: endpoint,
      data,
    });

    return response.data;
  }
}
