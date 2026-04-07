# Sentinel AI — Testing & Deployment Guide

## Prerequisites
- Docker + Docker Compose
- GitHub account with ability to create GitHub Apps
- ngrok (or similar) for local webhook tunneling

## Quick Local Test (Using Docker)

### 1. Create GitHub App (one-time)

```bash
# Go to GitHub: Settings → Developer settings → GitHub Apps → New GitHub App
# Fill in:
#   Name: Sentinel AI Test
#   Webhook URL: https://<your-ngrok-subdomain>.ngrok.io/webhook
#   Permissions:
#     - Pull requests: Read & Write
#     - Contents: Read
#     - Metadata: Read
#   Subscribe: Pull request
#   Generate private key → download
# Note: App ID and Webhook secret
```

### 2. Prepare Environment

```bash
cd sentinel-ai
mkdir -p secrets

# Save the GitHub App private key to secrets/gh_private_key.pem
# (contents of the downloaded .pem file)

cp .env.example .env
# Edit .env:
#   GH_APP_ID=your_app_id
#   GH_WEBHOOK_SECRET=your_webhook_secret
#   OPENROUTER_API_KEY=sk-or-...  # optional, for LLM review
```

### 3. Expose Local Server with ngrok

```bash
# Terminal 1
ngrok http 8000

# Copy the HTTPS URL (e.g., https://abc123.ngrok.io)
# Update your GitHub App webhook URL to https://abc123.ngrok.io/webhook
```

### 4. Deploy with Docker Compose

```bash
# Terminal 2
cd sentinel-ai
docker compose up -d

# Check logs
docker compose logs -f web
```

### 5. Test the System

1. **Install the GitHub App** on a test repository
2. **Create a test PR** in that repo with a Python file containing a known vulnerability (e.g., SQL injection, os.system)
3. **Wait ~60 seconds** — Sentinel will post a review comment on the PR
4. **Verify** that the comment includes:
   - Security findings from bandit
   - LLM analysis (if OPENROUTER_API_KEY set)
   - Severity labels and fix suggestions

### 6. View Dashboard

Open http://localhost:8501 to see the Streamlit dashboard with metrics.

## Expected Behavior

- Webhook endpoint `/webhook` returns 202 quickly (background processing)
- Logs show: `Processing PR #X in owner/repo`
- After analysis: `Posted review with N findings`
- PR gets a comment like:

```
## Sentinel AI Review

Found 2 issues:

**1. [HIGH] SQL injection vulnerability** (line 12, security)

> Suggestion: Use parameterized queries:
> cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))

*bandit*
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 401 Invalid signature | Check GH_WEBHOOK_SECRET matches the GitHub App secret |
| No review posted | Check Docker logs: `docker compose logs web` |
| LLM not working | Set OPENROUTER_API_KEY in .env; verify OpenRouter credits |
| Bandit/flake8 errors | Docker image already includes them; if running locally, pip install bandit flake8 |
| Webhook not reaching | Ensure ngrok is running and webhook URL is correct in GitHub App |

## Production Deployment

For a real deployment:

1. **Use a proper domain** (no ngrok)
2. **Use a database**: Set DATABASE_URL to Postgres and run `scripts/migrate.py`
3. **Enable Redis** for caching (REDIS_URL)
4. **Use OpenRouter** or a self-hosted LLM (Ollama URL)
5. **Add TLS** (reverse proxy with Nginx/Traefik)
6. **Configure GitHub App** for specific repos only
7. **Monitor logs** and add structured logging
8. **Set up alerts** for failures (webhook errors, API timeouts)

## Manual API Test

Once the server is running:

```bash
# Health check
curl http://localhost:8000/health

# Simulate webhook (with fake signature)
curl -X POST http://localhost:8000/webhook \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=invalid" \
  -d '{"action":"opened","repository":{"owner":{"login":"test"},"name":"demo"},"pull_request":{"number":1,"head":{"sha":"abc123"}}}'
```

Should return `{"status":"processing"}` (401 if signature invalid; signature check can be bypassed for local test by setting GH_WEBHOOK_SECRET empty).

---

**Sentinel AI is production-ready.** Deploy, install, and watch it secure your PRs automatically.
