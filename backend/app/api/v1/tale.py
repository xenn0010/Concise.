"""
TALE (Token-Budget-Aware LLM Reasoning) API Endpoints
Reduce output tokens by 60-70% while maintaining accuracy
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal, Dict, Any
import os

from app.services.tale_optimizer import get_tale_optimizer, EstimationStrategy
from app.middleware.auth import get_current_user
from app.models.user import User

router = APIRouter()


class TALEOptimizeRequest(BaseModel):
    """Request to optimize a prompt with TALE"""
    prompt: str = Field(..., description="The prompt to optimize", min_length=1)
    strategy: EstimationStrategy = Field(
        default="fixed",
        description="Budget estimation strategy: zero_shot, fixed, or adaptive"
    )
    target_budget: Optional[int] = Field(
        default=None,
        description="Manual token budget (overrides estimation)",
        ge=10,
        le=2000
    )


class TALEOptimizeResponse(BaseModel):
    """Response from TALE optimization"""
    optimized_prompt: str
    original_prompt: str
    estimated_budget: int
    budget_metadata: Dict[str, Any]
    prompt_additions: Dict[str, str]


class TALEValidateRequest(BaseModel):
    """Request to validate LLM output against budget"""
    output: str = Field(..., description="The LLM's output to validate")
    budget: int = Field(..., description="Token budget", ge=10)
    tolerance: float = Field(
        default=0.2,
        description="Budget tolerance (0.2 = allow 20% over)",
        ge=0.0,
        le=1.0
    )


class TALEValidateResponse(BaseModel):
    """Response from TALE validation"""
    within_budget: bool
    actual_tokens: int
    budget_tokens: int
    max_allowed_tokens: int
    budget_utilization: float
    tokens_saved: int
    exceeded_by: int


@router.post("/tale/optimize", response_model=TALEOptimizeResponse)
async def optimize_prompt(
    request: TALEOptimizeRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Optimize a prompt using TALE (Token-Budget-Aware LLM Reasoning)

    This endpoint:
    1. Estimates optimal token budget for the prompt
    2. Injects budget constraint into the prompt
    3. Returns optimized prompt that guides LLM to generate concise output

    Expected results:
    - 60-70% reduction in output tokens
    - 95%+ accuracy retention
    - Works with any LLM (GPT-4, Claude, etc.)

    Strategies:
    - "fixed": Fast heuristic-based estimation (no LLM call)
    - "zero_shot": LLM-based estimation (requires OpenAI API key, costs ~$0.0001/call)
    - "adaptive": User history-based (requires user data)

    Example:
    ```
    POST /v1/tale/optimize
    {
        "prompt": "Explain how binary search works",
        "strategy": "zero_shot"
    }
    ```

    Returns optimized prompt like:
    ```
    "Let's think step by step and use less than 150 tokens:

    Explain how binary search works

    Remember: Be concise, stay within 150 tokens."
    ```
    """
    try:
        optimizer = get_tale_optimizer()

        # For zero-shot strategy, create OpenAI client if API key is available
        llm_client = None
        if request.strategy == "zero_shot":
            openai_api_key = os.getenv("OPENAI_API_KEY")
            if openai_api_key:
                from openai import OpenAI
                llm_client = OpenAI(api_key=openai_api_key)
            else:
                # Fallback to fixed if no API key
                import logging
                logging.warning("Zero-shot strategy requires OPENAI_API_KEY, falling back to fixed strategy")

        result = optimizer.optimize_prompt(
            prompt=request.prompt,
            strategy=request.strategy,
            target_budget=request.target_budget,
            llm_client=llm_client
        )

        return TALEOptimizeResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"TALE optimization failed: {str(e)}"
        )


@router.post("/tale/validate", response_model=TALEValidateResponse)
async def validate_output(
    request: TALEValidateRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Validate that LLM output stayed within token budget

    Use this after receiving LLM response to check:
    - Did the LLM respect the budget?
    - How many tokens were saved?
    - Budget utilization percentage

    Example:
    ```
    POST /v1/tale/validate
    {
        "output": "Binary search is...",
        "budget": 150,
        "tolerance": 0.2
    }
    ```

    Returns validation result with compliance status.
    """
    try:
        optimizer = get_tale_optimizer()

        result = optimizer.validate_output(
            output=request.output,
            budget=request.budget,
            tolerance=request.tolerance
        )

        return TALEValidateResponse(**result)

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Output validation failed: {str(e)}"
        )


@router.get("/tale/info")
async def tale_info():
    """
    Get information about TALE optimization

    Returns details about the TALE framework, expected results,
    and usage instructions.
    """
    return {
        "name": "TALE (Token-Budget-Aware LLM Reasoning)",
        "version": "1.0.0",
        "description": "Reduce output tokens by 60-70% while maintaining accuracy",
        "research_paper": "https://arxiv.org/abs/2412.18547",
        "conference": "ACL 2025 (Findings)",
        "github": "https://github.com/GeniusHTX/TALE",
        "expected_results": {
            "token_reduction": "60-70%",
            "accuracy_retention": "95%+",
            "cost_savings": "59% (on output tokens)",
            "latency_impact": "minimal (estimation is fast)"
        },
        "strategies": {
            "fixed": {
                "description": "Heuristic-based budget estimation",
                "speed": "instant",
                "accuracy": "70% confidence",
                "best_for": "Most use cases"
            },
            "zero_shot": {
                "description": "LLM estimates its own budget",
                "speed": "1 extra LLM call",
                "accuracy": "85% confidence",
                "best_for": "Maximum accuracy"
            },
            "adaptive": {
                "description": "Uses user history for estimation",
                "speed": "instant",
                "accuracy": "85% confidence (with history)",
                "best_for": "Returning users"
            }
        },
        "compatible_models": [
            "GPT-4", "GPT-4o", "GPT-4o-mini",
            "Claude 3.5 Sonnet", "Claude 3 Opus",
            "Gemini Pro", "Llama 3.1",
            "All LLMs (LLM-agnostic)"
        ],
        "usage": {
            "step_1": "POST /v1/tale/optimize with your prompt",
            "step_2": "Send optimized_prompt to your LLM",
            "step_3": "POST /v1/tale/validate to check compliance",
            "step_4": "Enjoy 60-70% cost savings on output tokens"
        },
        "example_savings": {
            "scenario": "1 million API calls/month, 500 tokens output each",
            "baseline_cost": "$30,000 (GPT-4 @ $0.06/1K)",
            "tale_cost": "$9,000 (70% reduction)",
            "monthly_savings": "$21,000"
        }
    }
