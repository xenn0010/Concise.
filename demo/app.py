import os
import time
from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Concise SDK Demo", version="1.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

CONCISE_API_URL = os.getenv("CONCISE_API_URL", "http://localhost:8000")
CONCISE_API_KEY = os.getenv("CONCISE_API_KEY", "demo-key-12345")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

print(f"Concise API URL: {CONCISE_API_URL}")
print(f"Concise API Key configured: {bool(CONCISE_API_KEY)}")
print(f"OpenAI API Key configured: {bool(OPENAI_API_KEY)}")

class CompressRequest(BaseModel):
    text: str
    level: str = "auto"

class TALERequest(BaseModel):
    prompt: str
    strategy: str = "fixed"
    target_budget: Optional[int] = None

class FullOptimizationRequest(BaseModel):
    prompt: str
    model: str = "gpt-4"
    compression_level: str = "auto"
    tale_strategy: str = "fixed"
    execute_llm: bool = False

class BenchmarkRequest(BaseModel):
    prompts: list[str]
    model: str = "gpt-4"

GPT4_INPUT_COST = 0.03 / 1000
GPT4_OUTPUT_COST = 0.06 / 1000
GPT35_INPUT_COST = 0.0015 / 1000
GPT35_OUTPUT_COST = 0.002 / 1000

def get_pricing(model: str) -> tuple[float, float]:
    if "gpt-4" in model.lower():
        return GPT4_INPUT_COST, GPT4_OUTPUT_COST
    return GPT35_INPUT_COST, GPT35_OUTPUT_COST

def count_tokens_approx(text: str) -> int:
    return int(len(text.split()) * 1.3)

@app.get("/")
async def root():
    return {
        "name": "Concise SDK Demo",
        "version": "1.1.0",
        "features": ["compression", "tale", "benchmarks"],
        "status": "ready"
    }

@app.post("/api/compress")
async def compress_text(request: CompressRequest):
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{CONCISE_API_URL}/v1/compress",
            headers={"X-API-Key": CONCISE_API_KEY},
            json={
                "text": request.text,
                "level": request.level
            },
            timeout=30.0
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"Compression failed: {response.text}")

        result = response.json()

    elapsed_ms = (time.time() - start_time) * 1000

    return {
        "original_text": request.text,
        "compressed_text": result.get("compressed_text", result.get("compressedText", "")),
        "original_tokens": result.get("original_tokens", result.get("originalTokens", 0)),
        "compressed_tokens": result.get("compressed_tokens", result.get("compressedTokens", 0)),
        "tokens_saved": result.get("tokens_saved", result.get("tokensSaved", 0)),
        "compression_ratio": result.get("compression_ratio", result.get("compressionRatio", 1.0)),
        "strategy": result.get("strategy", "auto"),
        "compression_time_ms": elapsed_ms,
        "cache_hit": result.get("cache_hit", result.get("cacheHit", False))
    }

@app.post("/api/tale/optimize")
async def optimize_for_output(request: TALERequest):
    start_time = time.time()

    async with httpx.AsyncClient() as client:
        payload = {
            "prompt": request.prompt,
            "strategy": request.strategy
        }
        if request.target_budget:
            payload["target_budget"] = request.target_budget

        response = await client.post(
            f"{CONCISE_API_URL}/v1/tale/optimize",
            headers={"X-API-Key": CONCISE_API_KEY},
            json=payload,
            timeout=30.0
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=f"TALE optimization failed: {response.text}")

        result = response.json()

    elapsed_ms = (time.time() - start_time) * 1000

    return {
        "original_prompt": result.get("original_prompt", result.get("originalPrompt", request.prompt)),
        "optimized_prompt": result.get("optimized_prompt", result.get("optimizedPrompt", "")),
        "estimated_budget": result.get("estimated_budget", result.get("estimatedBudget", 0)),
        "budget_metadata": result.get("budget_metadata", result.get("budgetMetadata", {})),
        "prompt_additions": result.get("prompt_additions", result.get("promptAdditions", {})),
        "optimization_time_ms": elapsed_ms
    }

@app.post("/api/full-optimization")
async def full_optimization(request: FullOptimizationRequest):
    input_price, output_price = get_pricing(request.model)

    original_input_tokens = count_tokens_approx(request.prompt)

    compress_start = time.time()
    async with httpx.AsyncClient() as client:
        compress_response = await client.post(
            f"{CONCISE_API_URL}/v1/compress",
            headers={"X-API-Key": CONCISE_API_KEY},
            json={
                "text": request.prompt,
                "level": request.compression_level
            },
            timeout=30.0
        )
        compress_result = compress_response.json()
    compress_time = (time.time() - compress_start) * 1000

    compressed_text = compress_result.get("compressed_text", compress_result.get("compressedText", request.prompt))
    compressed_tokens = compress_result.get("compressed_tokens", compress_result.get("compressedTokens", original_input_tokens))

    tale_start = time.time()
    async with httpx.AsyncClient() as client:
        tale_response = await client.post(
            f"{CONCISE_API_URL}/v1/tale/optimize",
            headers={"X-API-Key": CONCISE_API_KEY},
            json={
                "prompt": compressed_text,
                "strategy": request.tale_strategy
            },
            timeout=30.0
        )
        tale_result = tale_response.json()
    tale_time = (time.time() - tale_start) * 1000

    optimized_prompt = tale_result.get("optimized_prompt", tale_result.get("optimizedPrompt", compressed_text))
    estimated_output_budget = tale_result.get("estimated_budget", tale_result.get("estimatedBudget", int(original_input_tokens * 2)))

    baseline_output_tokens = int(original_input_tokens * 5)

    baseline_input_cost = original_input_tokens * input_price
    baseline_output_cost = baseline_output_tokens * output_price
    baseline_total_cost = baseline_input_cost + baseline_output_cost

    optimized_input_cost = compressed_tokens * input_price
    optimized_output_cost = estimated_output_budget * output_price
    optimized_total_cost = optimized_input_cost + optimized_output_cost

    total_savings = baseline_total_cost - optimized_total_cost
    savings_percentage = (total_savings / baseline_total_cost) * 100

    llm_response = None
    actual_output_tokens = None
    actual_cost = None

    if request.execute_llm and OPENAI_API_KEY:
        try:
            openai_client = OpenAI(api_key=OPENAI_API_KEY)
            llm_start = time.time()
            completion = openai_client.chat.completions.create(
                model=request.model,
                messages=[{"role": "user", "content": optimized_prompt}],
                max_tokens=estimated_output_budget + 50
            )
            llm_time = (time.time() - llm_start) * 1000

            llm_response = completion.choices[0].message.content
            actual_output_tokens = completion.usage.completion_tokens
            actual_cost = (compressed_tokens * input_price) + (actual_output_tokens * output_price)

        except Exception as e:
            llm_response = f"Error: {str(e)}"

    return {
        "compression_step": {
            "original_text": request.prompt,
            "compressed_text": compressed_text,
            "original_tokens": original_input_tokens,
            "compressed_tokens": compressed_tokens,
            "tokens_saved": original_input_tokens - compressed_tokens,
            "compression_ratio": compress_result.get("compression_ratio", compress_result.get("compressionRatio", 0.5)),
            "time_ms": compress_time
        },
        "tale_step": {
            "optimized_prompt": optimized_prompt,
            "estimated_output_budget": estimated_output_budget,
            "baseline_estimated_output": baseline_output_tokens,
            "output_tokens_saved": baseline_output_tokens - estimated_output_budget,
            "strategy": request.tale_strategy,
            "time_ms": tale_time
        },
        "cost_analysis": {
            "baseline": {
                "input_tokens": original_input_tokens,
                "output_tokens": baseline_output_tokens,
                "input_cost": baseline_input_cost,
                "output_cost": baseline_output_cost,
                "total_cost": baseline_total_cost
            },
            "optimized": {
                "input_tokens": compressed_tokens,
                "output_tokens": estimated_output_budget,
                "input_cost": optimized_input_cost,
                "output_cost": optimized_output_cost,
                "total_cost": optimized_total_cost
            },
            "savings": {
                "input_tokens_saved": original_input_tokens - compressed_tokens,
                "output_tokens_saved": baseline_output_tokens - estimated_output_budget,
                "total_tokens_saved": (original_input_tokens + baseline_output_tokens) - (compressed_tokens + estimated_output_budget),
                "cost_saved": total_savings,
                "savings_percentage": savings_percentage
            },
            "model": request.model,
            "pricing": {
                "input_price_per_1k": input_price * 1000,
                "output_price_per_1k": output_price * 1000
            }
        },
        "llm_execution": {
            "executed": request.execute_llm,
            "response": llm_response,
            "actual_output_tokens": actual_output_tokens,
            "actual_cost": actual_cost
        } if request.execute_llm else None,
        "total_time_ms": compress_time + tale_time
    }

@app.get("/api/health")
async def health():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{CONCISE_API_URL}/health", timeout=5.0)
            backend_healthy = response.status_code == 200
    except:
        backend_healthy = False

    return {
        "status": "healthy" if backend_healthy else "degraded",
        "backend_connected": backend_healthy,
        "openai_configured": bool(OPENAI_API_KEY),
        "version": "1.1.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=3000)
