/**
 * TypeScript SDK Integration Tests
 * Tests real API calls against running backend
 */

const { Concise, OpenAI } = require('./typescript-sdk/dist/index.js');
const { AuthenticationError } = require('./typescript-sdk/dist/index.js');
const fs = require('fs');

// Load API key
const API_KEY = fs.readFileSync('/tmp/concise_test_key.txt', 'utf8').trim();
const BASE_URL = "http://localhost:8000/v1";

console.log("=".repeat(70));
console.log("TYPESCRIPT SDK INTEGRATION TESTS");
console.log("=".repeat(70));

async function runTests() {
  // Test 1: Client initialization
  console.log("\n1. Testing client initialization...");
  try {
    const client = new Concise({ apiKey: API_KEY, baseUrl: BASE_URL });
    console.log("   ✅ Client initialized");
  } catch (error) {
    console.log(`   ❌ Initialization failed: ${error.message}`);
  }

  // Test 2: Python code compression
  console.log("\n2. Testing Python code compression...");
  try {
    const client = new Concise({ apiKey: API_KEY, baseUrl: BASE_URL });
    const code = `def fibonacci(n):
    '''Calculate fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)
`;

    const result = await client.compress(code, 'auto');
    console.log("   ✅ Compression successful");
    console.log(`   - Original: ${result.originalTokens} tokens`);
    console.log(`   - Compressed: ${result.compressedTokens} tokens`);
    console.log(`   - Saved: ${result.tokensSaved} tokens (${((1-result.compressionRatio)*100).toFixed(1)}%)`);
    console.log(`   - Strategy: ${result.strategy}`);
    console.log(`   - Time: ${result.compressionTimeMs.toFixed(0)}ms`);
    if (result.cacheHit) {
      console.log("   - Cache: HIT (instant!)");
    }
  } catch (error) {
    console.log(`   ❌ Compression failed: ${error.message}`);
    console.error(error);
  }

  // Test 3: Natural language compression
  console.log("\n3. Testing natural language compression...");
  try {
    const client = new Concise({ apiKey: API_KEY, baseUrl: BASE_URL });
    const text = "FastAPI is a modern, fast web framework for building APIs with Python 3.8+";

    const result = await client.compress(text, 'aggressive');
    console.log("   ✅ Compression successful");
    console.log(`   - Original: ${result.originalTokens} tokens`);
    console.log(`   - Compressed: ${result.compressedTokens} tokens`);
    console.log(`   - Saved: ${result.tokensSaved} tokens (${((1-result.compressionRatio)*100).toFixed(1)}%)`);
    console.log(`   - Strategy: ${result.strategy}`);
    console.log(`   - Time: ${result.compressionTimeMs.toFixed(0)}ms`);
    if (result.cacheHit) {
      console.log("   - Cache: HIT");
    }
  } catch (error) {
    console.log(`   ❌ Compression failed: ${error.message}`);
    console.error(error);
  }

  // Test 4: Cache test (repeat compression)
  console.log("\n4. Testing cache (repeat compression)...");
  try {
    const client = new Concise({ apiKey: API_KEY, baseUrl: BASE_URL });
    const text = "FastAPI is a modern, fast web framework for building APIs with Python 3.8+";

    const result = await client.compress(text, 'aggressive');
    if (result.cacheHit) {
      console.log(`   ✅ Cache working! Response time: ${result.compressionTimeMs.toFixed(1)}ms`);
    } else {
      console.log("   ⚠️  Cache miss (expected hit)");
    }
  } catch (error) {
    console.log(`   ❌ Cache test failed: ${error.message}`);
  }

  // Test 5: Different compression levels
  console.log("\n5. Testing different compression levels...");
  try {
    const client = new Concise({ apiKey: API_KEY, baseUrl: BASE_URL });
    const testText = "The quick brown fox jumps over the lazy dog. This is a test sentence.";

    for (const level of ['conservative', 'balanced', 'aggressive']) {
      const result = await client.compress(testText, level);
      console.log(`   - ${level.padEnd(15)}: ${result.compressedTokens.toString().padStart(3)} tokens (${result.compressionRatio.toFixed(2)}x)`);
    }
  } catch (error) {
    console.log(`   ❌ Level testing failed: ${error.message}`);
  }

  // Test 6: Invalid API key
  console.log("\n6. Testing invalid API key handling...");
  try {
    const badClient = new Concise({ apiKey: "invalid-key", baseUrl: BASE_URL });
    await badClient.compress("test");
    console.log("   ❌ Should have raised AuthenticationError");
  } catch (error) {
    if (error.name === 'AuthenticationError') {
      console.log(`   ✅ AuthenticationError raised correctly: ${error.message}`);
    } else {
      console.log(`   ⚠️  Different error: ${error.message}`);
    }
  }

  // Test 7: OpenAI wrapper initialization
  console.log("\n7. Testing OpenAI wrapper...");
  try {
    const openaiClient = new OpenAI({ apiKey: API_KEY, baseUrl: BASE_URL });
    console.log("   ✅ OpenAI wrapper initialized");
    console.log(`   - Has chat attribute: ${!!openaiClient.chat}`);
    console.log(`   - Has completions: ${!!openaiClient.chat.completions}`);
  } catch (error) {
    console.log(`   ❌ OpenAI wrapper failed: ${error.message}`);
  }

  console.log("\n" + "=".repeat(70));
  console.log("INTEGRATION TESTS COMPLETE");
  console.log("=".repeat(70));
}

runTests().catch(err => {
  console.error("Test suite failed:", err);
  process.exit(1);
});
