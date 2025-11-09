/**
 * Concise TypeScript SDK
 * Official TypeScript/JavaScript client for the Concise API - Token compression for LLMs
 */

export { Concise } from './client';
export { OpenAI } from './openai';
export {
  ConciseError,
  AuthenticationError,
  APIError,
  RateLimitError,
  NetworkError,
} from './exceptions';
export type {
  CompressionLevel,
  CompressionResult,
  CompressRequest,
  ChatMessage,
  ChatCompletionRequest,
  ChatCompletionResponse,
  ConciseConfig,
  HealthResponse,
} from './types';
