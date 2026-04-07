# Contributing to Sentinel AI

Thanks for considering contributions! Please follow these guidelines.

## Setup

1. Fork and clone
2. `pip install -r requirements.txt`
3. Copy `.env.example` to `.env` and fill values (you can use Ollama for LLM to avoid API keys)
4. Run `docker compose up -d` for Postgres + Redis (optional)
5. Run `uvicorn sentinel_ai.main:app --reload` for API
6. Run `streamlit run dashboard.py` for UI

## Code Style

- Python: formatted with `black`, lint with `ruff`
- Type hints required for all functions
- Run `pre-commit install` if available (coming soon)

## Testing

```bash
pytest tests/ -v --cov=sentinel_ai
```

Aim for >80% coverage.

## Pull Request Process

1. Open an issue first for large changes
2. Create a feature branch
3. Make changes, add tests
4. Ensure CI passes (lint, type-check, tests)
5. Open PR with clear description

## Adding New Scanners

Implement a function in `sentinel_ai/scanners.py`:

```python
def run_mytool(code: str) -> List[Dict]:
    # analyze code, return list of findings: {tool, severity, line, message}
    pass
```

Then add it to `scan_file()`.

## LLM Prompts

Edit `SYSTEM_PROMPT` and `USER_PROMPT_TEMPLATE` in `llm_reviewer.py` to change review behavior.

## License

By contributing, you agree to MIT license.
