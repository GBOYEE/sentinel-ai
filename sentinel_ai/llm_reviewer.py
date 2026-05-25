"""LLM-based code reviewer using OpenRouter or Ollama."""

import json
import logging
from typing import List, Dict, Any, Optional

from sentinel_ai.config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OLLAMA_BASE_URL, ENABLE_LLM_REVIEW

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are an expert code security and quality reviewer. Analyze the provided code diff and identify issues:

1. SECURITY vulnerabilities (SQL injection, XSS, auth flaws, path traversal, etc.)
2. CODE QUALITY problems (complexity, duplication, naming, maintainability)
3. PERFORMANCE concerns (inefficient algorithms, N+1 queries, etc.)
4. BEST PRACTICES violations (error handling, logging, documentation)

For each issue, provide:
- line number (if applicable)
- severity: critical/high/medium/low/info
- category: security|quality|performance|best-practice
- description: clear explanation
- suggestion: concrete fix or improvement

Be concise but thorough. Return JSON with a "findings" key containing an array of objects.
Each object must have: line, severity, category, description, suggestion.
"""

USER_PROMPT_TEMPLATE = """Review this code change:

Filename: {filename}
Diff:
```diff
{diff}
```

Context (surrounding code):
```python
{context}
```

Return JSON: {{"findings": [...]}}
"""


async def review_code_with_llm(diff: str, filename: str, context: str = "") -> List[Dict[str, Any]]:
    """Use LLM to review code and return findings (async version)."""
    if not ENABLE_LLM_REVIEW:
        return []

    try:
        from openai import AsyncOpenAI
    except ImportError:
        logger.error("openai package not installed")
        return []

    # Prefer OpenRouter if key present, else Ollama
    if OPENROUTER_API_KEY:
        client = AsyncOpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        model = OPENROUTER_MODEL
    else:
        client = AsyncOpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        model = "llama3.1:8b"

    user_prompt = USER_PROMPT_TEMPLATE.format(
        filename=filename,
        diff=diff[:3000],  # Limit diff size
        context=context[:2000] if context else "(no additional context)",
    )

    try:
        response = await client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1500,
        )
        content = response.choices[0].message.content
        if not content:
            return []
        
        # Parse JSON response
        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*([\s\S]+?)\s*```', content)
            if json_match:
                data = json.loads(json_match.group(1))
            else:
                logger.warning(f"Could not parse LLM response as JSON: {content[:200]}")
                return []

        findings = data.get("findings", [])
        for f in findings:
            f["tool"] = "llm"
        return findings
    except Exception as e:
        logger.error(f"LLM review error: {e}")
        return []


def review_code_with_llm_sync(diff: str, filename: str, context: str = "") -> List[Dict[str, Any]]:
    """Synchronous wrapper for LLM review (for non-async contexts)."""
    import asyncio
    try:
        loop = asyncio.get_running_loop()
        # We're in an async context, create a task
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, review_code_with_llm(diff, filename, context))
            return future.result(timeout=60)
    except RuntimeError:
        # No running loop, safe to use asyncio.run
        return asyncio.run(review_code_with_llm(diff, filename, context))
