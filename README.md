# 🛡️ Sentinel AI — PR Security & Quality Reviewer

**AI-powered automated code review for every pull request.**

Sentinel AI combines static analysis (bandit, flake8, semgrep) with LLM reasoning to catch security vulnerabilities, code quality issues, and best practice violations — automatically on every PR.

## Features

- **Multi-scanner pipeline** — bandit (security), flake8 (quality), semgrep (patterns)
- **AI reasoning** — LLM explains *why* something is a problem and *how* to fix it
- **Inline review comments** — findings appear as line-level comments on the PR, not a wall of text
- **Smart severity** — critical/high findings request changes, medium/low are comments
- **Dashboard** — Streamlit UI for monitoring all reviews and findings
- **Zero config** — works out of the box on any Python repo

## How It Works

1. Install the GitHub App on your repos
2. Open or update a PR
3. Sentinel AI scans all changed files
4. Findings appear as inline review comments within seconds
5. Critical/high issues block merge (request changes), medium/low are advisory

## Installation

### From GitHub Marketplace

1. Visit [Sentinel AI on GitHub Marketplace](https://github.com/marketplace/sentinel-ai)
2. Click **Install**
3. Select repositories (or all repos)
4. Done — open a PR and watch it work

### Self-Hosted

```bash
# Clone and install
git clone https://github.com/GBOYEE/sentinel-ai.git
cd sentinel-ai
pip install -e ".[scanners]"

# Configure
cp .env.example .env
# Edit .env with your GitHub App credentials

# Run
uvicorn sentinel_ai.main:app --host 0.0.0.0 --port 8000
```

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `GH_APP_ID` | Yes | GitHub App ID |
| `GH_APP_PRIVATE_KEY` | Yes | Path to private key PEM file |
| `GH_WEBHOOK_SECRET` | Yes | Webhook secret |
| `OPENROUTER_API_KEY` | No | OpenRouter API key (for LLM review) |
| `OPENROUTER_MODEL` | No | Model (default: `openai/gpt-4o-mini`) |
| `ENABLE_STATIC_ANALYSIS` | No | Enable bandit/flake8/semgrep (default: true) |
| `ENABLE_LLM_REVIEW` | No | Enable LLM review (default: true) |
| `DATABASE_URL` | No | Database (default: SQLite) |

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Free** | $0 | Static analysis only (bandit + flake8), 10 repos |
| **Pro** | $9/repo/mo | + LLM reasoning, unlimited repos, dashboard |
| **Team** | $29/repo/mo | + Priority support, custom rules, Slack integration |

## Supported Languages

- Python (full: bandit + flake8 + semgrep + LLM)
- JavaScript/TypeScript (LLM review)
- Go, Rust, Java, Ruby (LLM review)

## Architecture

```
GitHub PR → Webhook → FastAPI → Scanner Pipeline → LLM Review → Inline Comments
                                    ↓
                              SQLite/PostgreSQL
                                    ↓
                              Streamlit Dashboard
```

## Development

```bash
# Run tests
pytest tests/ -v

# Run dashboard
streamlit run dashboard.py

# Run locally
uvicorn sentinel_ai.main:app --reload
```

## License

MIT
