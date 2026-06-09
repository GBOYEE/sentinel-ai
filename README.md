<div align="center">

# 🛡️ Sentinel AI

**AI-Powered Automated Code Review for GitHub**

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![GitHub App](https://img.shields.io/badge/GitHub-App-181717?logo=github&logoColor=white)](https://github.com/settings/apps)

*Catch security vulnerabilities, code quality issues, and bad practices — automatically on every pull request.*

[Install Free](https://github.com/marketplace/sentinel-ai) · [Documentation](#-quick-start) · [Report Bug](https://github.com/GBOYEE/sentinel-ai/issues)

</div>

---

## ✨ How It Works

```
Open PR → Sentinel AI scans → Inline comments appear in seconds
```

<div align="center">

| 🔍 Scans | 💬 Reviews | 🛡️ Catches |
|----------|-----------|-----------|
| bandit, flake8, semgrep + LLM | Inline PR comments on specific lines | SQL injection, XSS, hardcoded secrets, eval misuse, command injection, 50+ patterns |

</div>

## 🚀 Quick Start

### Install from GitHub Marketplace (recommended)

1. Go to [GitHub Marketplace](https://github.com/marketplace/sentinel-ai)
2. Click **Install**
3. Select repositories
4. Open a PR — Sentinel AI reviews automatically!

### Self-Hosted

```bash
git clone https://github.com/GBOYEE/sentinel-ai.git
cd sentinel-ai
pip install -e ".[scanners]"
cp .env.example .env
# Edit .env with your GitHub App credentials
uvicorn sentinel_ai.main:app --host 0.0.0.0 --port 8000
```

### Configure

Create a [GitHub App](https://github.com/settings/apps/new) with:
- **Webhook URL**: `https://your-server.com/webhook`
- **Permissions**: Pull Requests (Read & Write), Contents (Read), Issues (Read & Write)
- **Events**: Pull request

```env
GH_APP_ID=123456
GH_APP_PRIVATE_KEY=/path/to/private-key.pem
GH_WEBHOOK_SECRET=your-secret
OPENROUTER_API_KEY=sk-or-...
```

## 📋 Pricing

| Plan | Price | Features |
|------|-------|---------|
| **Free** | $0 | Static analysis (bandit + flake8), up to 5 repos |
| **Pro** | $9/repo/mo | + LLM reasoning, unlimited repos, all languages |
| **Team** | $29/repo/mo | + Custom rules, Slack, SSO, priority support |

## 🧠 What It Catches

### Security
- SQL injection, XSS, CSRF
- Command injection (`os.system`, `subprocess.shell=True`)
- Hardcoded secrets (API keys, passwords)
- `eval()` / `exec()` on user input
- Path traversal, SSRF
- Insecure deserialization

### Code Quality
- Bare except blocks
- Unused imports / variables
- Missing type hints
- Functions too complex
- Missing error handling
- Debug mode left on

### Best Practices
- No input validation
- Missing documentation
- Hardcoded config values
- Wrong crypto algorithms

## 🏗️ Architecture

```
GitHub PR → Webhook → FastAPI → Scanner Pipeline → LLM Review → Inline Comments
                                    ↓
                              SQLite/PostgreSQL
                                    ↓
                              Streamlit Dashboard
```

**Scanner Pipeline:**
1. **bandit** — Python security analysis
2. **flake8** — Code style & quality
3. **semgrep** — Pattern-based multi-language analysis
4. **LLM Review** — AI reasoning explains *why* and *how to fix*

## 📊 Supported Languages

| Language | Static Analysis | LLM Review |
|----------|----------------|------------|
| Python | ✅ Full | ✅ |
| JavaScript | ⚡ semgrep | ✅ |
| TypeScript | ⚡ semgrep | ✅ |
| Go | ⚡ semgrep | ✅ |
| Rust | ⚡ semgrep | ✅ |
| Java | ⚡ semgrep | ✅ |
| Ruby | ⚡ semgrep | ✅ |

## 🧪 Development

```bash
# Run tests
pytest tests/ -v

# Run locally with auto-reload
uvicorn sentinel_ai.main:app --reload

# Run dashboard
streamlit run dashboard.py
```

## 📝 API Reference

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Service info |
| `/health` | GET | Health check |
| `/webhook` | POST | GitHub webhook receiver |
| `/review` | POST | Manual review trigger |

## 🤝 Contributing

Issues and PRs welcome! See [CONTRIBUTING.md](CONTRIBUTING.md).

## 📄 License

MIT © 2026 [XANDERCORP](https://github.com/XANDERCORP)
