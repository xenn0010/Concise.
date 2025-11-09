"""
TALE (Token-Budget-Aware LLM Reasoning) Integration
Implementation of TALE-EP (Early Pruning with Zero-shot Estimator)

Based on: "Token-Budget-Aware LLM Reasoning" (ACL 2025)
Paper: https://arxiv.org/abs/2412.18547
GitHub: https://github.com/GeniusHTX/TALE

Reduces output tokens by 60-70% while maintaining accuracy.
"""

import time
from typing import Dict, Any, Optional, Literal
from dataclasses import dataclass
import tiktoken


EstimationStrategy = Literal["zero_shot", "fixed", "adaptive"]


@dataclass
class BudgetEstimate:
    """Result of token budget estimation"""
    estimated_tokens: int
    confidence: float  # 0.0 to 1.0
    reasoning: str
    strategy_used: EstimationStrategy


class TALEOptimizer:
    """
    Token-Budget-Aware LLM Reasoning Optimizer

    Implements TALE-EP approach:
    1. Estimate optimal token budget for the query
    2. Inject budget constraint into prompt
    3. Guide LLM to generate concise output

    Results: 60-70% output token reduction with <5% accuracy drop
    """

    def __init__(self, model: str = "gpt-3.5-turbo"):
        self.tokenizer = tiktoken.encoding_for_model(model)

        # Budget estimation prompts
        # GPT-5 optimized prompt - more direct and clear
        self.estimation_prompt_template = """How many output tokens do you need to answer this question?

Question: {question}

Reply with just a number between 50-500."""

        # Constrained generation template (TALE-EP format)
        self.constrained_prompt_template = """Let's think step by step and use less than {budget} tokens:

{original_prompt}

Remember: Be concise, stay within {budget} tokens."""

    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.tokenizer.encode(text))

    def estimate_budget_zero_shot(
        self,
        prompt: str,
        llm_client: Any = None
    ) -> BudgetEstimate:
        """
        TALE-EP Zero-shot Estimator

        Uses the LLM itself to estimate required tokens.
        This is the core TALE innovation - the model knows
        how complex the question is before answering.

        Args:
            prompt: User's original prompt
            llm_client: Optional LLM client to call for estimation
                       If None, uses heuristic estimation

        Returns:
            BudgetEstimate with token count and confidence
        """
        if llm_client is None:
            # Fallback to heuristic if no LLM client provided
            return self._estimate_budget_heuristic(prompt)

        # Ask LLM to estimate tokens needed
        estimation_prompt = self.estimation_prompt_template.format(
            question=prompt[:500]  # Truncate very long prompts
        )

        try:
            # Call LLM for zero-shot estimation
            # Using GPT-5 for superior estimation accuracy
            # Note: GPT-5 doesn't support max_completion_tokens for very short responses
            response = llm_client.chat.completions.create(
                model="gpt-5",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that estimates token budgets. Reply with ONLY a number."
                    },
                    {
                        "role": "user",
                        "content": estimation_prompt
                    }
                ]
            )

            # Parse the response
            estimated_text = response.choices[0].message.content.strip()

            # Extract number from response (handles "150" or "150 tokens" etc)
            import re
            numbers = re.findall(r'\d+', estimated_text)
            if numbers:
                estimated_tokens = int(numbers[0])

                # Sanity check - keep within reasonable bounds
                if estimated_tokens < 20:
                    estimated_tokens = 50
                elif estimated_tokens > 1000:
                    estimated_tokens = 500

                return BudgetEstimate(
                    estimated_tokens=estimated_tokens,
                    confidence=0.9,  # High confidence for LLM estimation
                    reasoning="LLM-based zero-shot estimation",
                    strategy_used="zero_shot"
                )
            else:
                # Couldn't parse, fallback
                return self._estimate_budget_heuristic(prompt)

        except Exception as e:
            # Fallback to heuristic on error
            import logging
            logging.warning(f"Zero-shot estimation failed: {e}, falling back to heuristic")
            return self._estimate_budget_heuristic(prompt)

    def _estimate_budget_heuristic(self, prompt: str) -> BudgetEstimate:
        """
        Heuristic-based budget estimation

        Uses prompt characteristics to estimate output tokens:
        - Simple Q&A: 50-100 tokens
        - Code generation: 150-300 tokens
        - Complex reasoning: 200-400 tokens
        - Long explanations: 300-500 tokens
        """
        prompt_tokens = self.count_tokens(prompt)
        prompt_lower = prompt.lower()

        # Detect task type
        is_code = any(kw in prompt_lower for kw in [
            "code", "function", "class", "implement", "write a program"
        ])
        is_reasoning = any(kw in prompt_lower for kw in [
            "explain", "why", "how does", "step by step", "reasoning"
        ])
        is_list = any(kw in prompt_lower for kw in [
            "list", "enumerate", "what are", "give me"
        ])

        # Base estimation
        if is_code:
            base_budget = 200
            reasoning = "Code generation task detected"
        elif is_reasoning:
            base_budget = 150
            reasoning = "Reasoning/explanation task detected"
        elif is_list:
            base_budget = 100
            reasoning = "List/enumeration task detected"
        else:
            base_budget = 75
            reasoning = "Simple Q&A task detected"

        # Adjust based on prompt complexity
        if prompt_tokens > 500:
            base_budget = int(base_budget * 1.5)
            reasoning += " (complex prompt)"
        elif prompt_tokens > 200:
            base_budget = int(base_budget * 1.2)
            reasoning += " (moderate prompt)"

        # Add buffer (TALE paper shows some elasticity needed)
        final_budget = int(base_budget * 1.2)

        return BudgetEstimate(
            estimated_tokens=final_budget,
            confidence=0.7,  # Moderate confidence for heuristic
            reasoning=reasoning,
            strategy_used="fixed"
        )

    def _estimate_budget_adaptive(
        self,
        prompt: str,
        user_history: Optional[Dict[str, Any]] = None
    ) -> BudgetEstimate:
        """
        Adaptive estimation based on user history

        If we have data on similar queries from this user,
        we can estimate more accurately.
        """
        # Start with heuristic
        base_estimate = self._estimate_budget_heuristic(prompt)

        if user_history is None:
            return base_estimate

        # Adjust based on user's typical response preferences
        avg_user_tokens = user_history.get("avg_output_tokens", 0)

        if avg_user_tokens > 0:
            # Blend heuristic with user history
            adjusted_budget = int(
                0.7 * base_estimate.estimated_tokens +
                0.3 * avg_user_tokens
            )

            return BudgetEstimate(
                estimated_tokens=adjusted_budget,
                confidence=0.85,  # Higher confidence with history
                reasoning=f"{base_estimate.reasoning} + user history",
                strategy_used="adaptive"
            )

        return base_estimate

    def optimize_prompt(
        self,
        prompt: str,
        strategy: EstimationStrategy = "fixed",
        target_budget: Optional[int] = None,
        user_history: Optional[Dict[str, Any]] = None,
        llm_client: Any = None
    ) -> Dict[str, Any]:
        """
        Apply TALE optimization to a prompt

        This is the main entry point for TALE integration.

        Args:
            prompt: Original user prompt
            strategy: Budget estimation strategy
                - "zero_shot": Ask LLM to estimate (requires llm_client)
                - "fixed": Use heuristic estimation
                - "adaptive": Use user history if available
            target_budget: Manual budget override (skip estimation)
            user_history: Optional user data for adaptive estimation
            llm_client: Optional LLM client for zero-shot estimation

        Returns:
            Dict containing:
                - optimized_prompt: Prompt with budget constraint
                - estimated_budget: Token budget
                - original_prompt: Original prompt (for reference)
                - budget_metadata: Estimation details
        """
        start_time = time.time()

        # Step 1: Estimate budget (Phase 1 of TALE)
        if target_budget is not None:
            # Manual budget provided
            budget_estimate = BudgetEstimate(
                estimated_tokens=target_budget,
                confidence=1.0,
                reasoning="Manual budget provided by user",
                strategy_used=strategy
            )
        elif strategy == "zero_shot":
            budget_estimate = self.estimate_budget_zero_shot(prompt, llm_client)
        elif strategy == "adaptive":
            budget_estimate = self._estimate_budget_adaptive(prompt, user_history)
        else:  # fixed
            budget_estimate = self._estimate_budget_heuristic(prompt)

        # Step 2: Construct constrained prompt (Phase 2 of TALE)
        optimized_prompt = self.constrained_prompt_template.format(
            budget=budget_estimate.estimated_tokens,
            original_prompt=prompt
        )

        optimization_time = (time.time() - start_time) * 1000

        return {
            "optimized_prompt": optimized_prompt,
            "original_prompt": prompt,
            "estimated_budget": budget_estimate.estimated_tokens,
            "budget_metadata": {
                "confidence": budget_estimate.confidence,
                "reasoning": budget_estimate.reasoning,
                "strategy": budget_estimate.strategy_used,
                "optimization_time_ms": round(optimization_time, 2)
            },
            "prompt_additions": {
                "prefix": f"Let's think step by step and use less than {budget_estimate.estimated_tokens} tokens:",
                "suffix": f"Remember: Be concise, stay within {budget_estimate.estimated_tokens} tokens."
            }
        }

    def validate_output(
        self,
        output: str,
        budget: int,
        tolerance: float = 0.2
    ) -> Dict[str, Any]:
        """
        Validate that LLM stayed within budget

        Args:
            output: LLM's generated output
            budget: The token budget
            tolerance: Allow budget to exceed by this % (0.2 = 20%)

        Returns:
            Validation result with compliance status
        """
        actual_tokens = self.count_tokens(output)
        max_allowed = int(budget * (1 + tolerance))
        within_budget = actual_tokens <= max_allowed

        return {
            "within_budget": within_budget,
            "actual_tokens": actual_tokens,
            "budget_tokens": budget,
            "max_allowed_tokens": max_allowed,
            "budget_utilization": round(actual_tokens / budget, 2),
            "tokens_saved": max(0, budget - actual_tokens),
            "exceeded_by": max(0, actual_tokens - max_allowed)
        }


# Singleton instance
_tale_optimizer: Optional[TALEOptimizer] = None


def get_tale_optimizer(model: str = "gpt-3.5-turbo") -> TALEOptimizer:
    """Get or create global TALE optimizer instance"""
    global _tale_optimizer
    if _tale_optimizer is None:
        _tale_optimizer = TALEOptimizer(model=model)
    return _tale_optimizer
