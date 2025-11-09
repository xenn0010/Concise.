/**
 * Exception classes for Concise SDK
 */

export class ConciseError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'ConciseError';
  }
}

export class AuthenticationError extends ConciseError {
  constructor(message: string) {
    super(message);
    this.name = 'AuthenticationError';
  }
}

export class APIError extends ConciseError {
  statusCode?: number;

  constructor(message: string, statusCode?: number) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
  }
}

export class RateLimitError extends ConciseError {
  constructor(message: string) {
    super(message);
    this.name = 'RateLimitError';
  }
}

export class NetworkError extends ConciseError {
  constructor(message: string) {
    super(message);
    this.name = 'NetworkError';
  }
}
