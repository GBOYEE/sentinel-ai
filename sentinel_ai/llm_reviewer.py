"""LLM-based code reviewer using OpenRouter or Ollama."""

import os
from typing import List, Dict, Any
from openai import OpenAI
from config import OPENROUTER_API_KEY, OPENROUTER_MODEL, OLLAMA_BASE_URL, ENABLE_LLM_REVIEW


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

Be concise but thorough. Return JSON list of findings.
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

Identify all issues and return as JSON array of objects with keys: line, severity, category, description, suggestion.
"""


def review_code_with_llm(diff: str, filename: str, context: str = "") -> List[Dict[str, Any]]:
    """Use LLM to review code and return findings."""
    if not ENABLE_LLM_REVIEW:
        return []

    # Prefer OpenRouter if key present, else Ollama
    if OPENROUTER_API_KEY:
        client = OpenAI(api_key=OPENROUTER_API_KEY, base_url="https://openrouter.ai/api/v1")
        model = OPENROUTER_MODEL
    else:
        client = OpenAI(base_url=OLLAMA_BASE_URL, api_key="ollama")
        model = "llama3.1:8b"  # or phi3:mini

    user_prompt = USER_PROMPT_TEMPLATE.format(
        filename=filename,
        diff=diff,
        context=context or "(no additional context)"
    )

    try:
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.1,
            max_tokens=1500,
            response_format={"type": "json_object"},
        )
        import json
        content = response.choices[0].message.content
        data = json.loads(content)
        # Expect {"findings": [...]}
        findings = data.get("findings", [])
        for f in findings:
            f["tool"] = "llm"
        return findings
    except Exception as e:
        return [{"tool": "llm", "severity": "error", "message": str(e)}]
