"""Test text compression for large AI agent inputs"""
import requests

API_KEY = "csk_live_x3xPv7y5L3FbUBM_1gebMM8vlibydeXSsmvYPez56ak"

# Test 1: Large system prompt (real-world example)
large_system_prompt = """You are an expert software engineer with deep knowledge of multiple programming languages, frameworks, and best practices. Your role is to assist developers with their technical challenges and provide high-quality solutions.

When answering questions, follow these guidelines:
1. Always prioritize correctness and security in your recommendations
2. Provide clear explanations with relevant code examples when appropriate
3. Consider edge cases and potential issues that may arise
4. Explain trade-offs between different approaches when multiple solutions exist
5. Use industry-standard best practices and follow established design patterns
6. Write code that is maintainable, scalable, and well-documented
7. If you are uncertain about something, admit it rather than providing incorrect information
8. Consider performance implications of your suggestions
9. Be aware of common security vulnerabilities like SQL injection, XSS, CSRF, and others
10. Suggest testing strategies to ensure code reliability

You have expertise in the following areas:
- Backend development: Python, Java, Node.js, Go, Rust, C++
- Frontend development: React, Vue, Angular, TypeScript, JavaScript
- Databases: PostgreSQL, MySQL, MongoDB, Redis
- DevOps: Docker, Kubernetes, CI/CD, AWS, Azure, GCP
- Architecture: Microservices, REST APIs, GraphQL, Event-driven systems
- Testing: Unit tests, integration tests, end-to-end tests
- Security: Authentication, authorization, encryption, secure coding practices

Always provide responses that are professional, accurate, and helpful. Your goal is to help developers become better at their craft while solving their immediate problems effectively."""

# Test 2: RAG documentation context
documentation_context = """# FastAPI Application Development Guide

## Introduction
FastAPI is a modern, fast (high-performance) web framework for building APIs with Python 3.7+ based on standard Python type hints. It is one of the fastest Python frameworks available, on par with NodeJS and Go, thanks to Starlette for the web parts and Pydantic for the data parts.

## Key Features
- Fast to code: Increase the speed to develop features by about 200% to 300%
- Fewer bugs: Reduce about 40% of human (developer) induced errors
- Intuitive: Great editor support with completion everywhere and less time debugging
- Easy: Designed to be easy to use and learn with less time reading documentation
- Short: Minimize code duplication with multiple features from each parameter declaration
- Robust: Get production-ready code with automatic interactive documentation
- Standards-based: Based on and fully compatible with the open standards for APIs: OpenAPI and JSON Schema

## Installation
To install FastAPI, you need to install both fastapi and an ASGI server like uvicorn. You can install them using pip with the following command: pip install fastapi uvicorn[standard]

## Basic Example
Here is a simple example of a FastAPI application that demonstrates the basic syntax and structure. This example creates a simple API with a single endpoint that returns a JSON response.

## Request Validation
FastAPI uses Pydantic for data validation. When you declare request parameters with Python type hints, FastAPI will automatically validate the incoming data, convert it to the appropriate type, and provide helpful error messages if the data is invalid. This saves you from writing boilerplate validation code.

## Dependency Injection
FastAPI has a powerful but intuitive dependency injection system that makes it easy to share logic across endpoints, manage database connections, handle authentication, and more. Dependencies are just Python functions that can be reused across your application.

## Error Handling
You can create custom exception handlers in FastAPI to return specific error responses for different types of exceptions. This allows you to provide consistent error messages across your API and handle errors gracefully.

## Testing
FastAPI makes it easy to write tests for your API using the TestClient from starlette.testclient. The TestClient allows you to make requests to your application without running a server, making your tests fast and reliable."""

# Test 3: Conversation history
conversation = """User: How do I set up authentication in my API?