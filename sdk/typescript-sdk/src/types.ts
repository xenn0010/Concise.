/**
 * Type definitions for Concise SDK
 */

export type CompressionLevel = 'auto' | 'aggressive' | 'balanced' | 'conservative';
export type EstimationStrategy = 'fixed' | 'zero_shot' | 'adaptive';

export interface CompressionResult {
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

export interface CompressRequest {
  text: string;
  level?: CompressionLevel;
}

export interface ChatMessage {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

export interface ChatCompletionRequest {
  model: string;
  messages: ChatMessage[];
  temperature?: number;
  maxTokens?: number;
  stream?: boolean;
  compressionEnabled?: boolean;
  compressionLevel?: CompressionLevel;
  [key: string]: any;
}

export interface ChatCompletionResponse {
  id: string;
  object: string;
  created: number;
  model: string;
  choices: Array<{
    index: number;
    message: ChatMessage;
    finishReason: string;
  }>;
  usage: {
    promptTokens: number;
    completionTokens: number;
    totalTokens: number;
  };
  compressionMetadata?: {
    originalTokens: number;
    compressedTokens: number;
    tokensSaved: number;
    compressionRatio: number;
    strategy: string;
    compressionTimeMs: number;
  };
}

export interface ConciseConfig {
  apiKey?: string;
  baseUrl?: string;
  timeout?: number;
}

export interface HealthResponse {
  status: string;
  version: string;
  environment: string;
}

export interface TALEOptimizeResult {
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

export interface TALEValidateResult {
  withinBudget: boolean;
  actualTokens: number;
  budgetTokens: number;
  maxAllowedTokens: number;
  budgetUtilization: number;
  tokensSaved: number;
  exceededBy: number;
}

export interface TALEOptimizeRequest {
  prompt: string;
  strategy?: EstimationStrategy;
  targetBudget?: number;
}

export interface TALEValidateRequest {
  output: string;
  budget: number;
  tolerance?: number;
}
