# Deployment & Testing Guide — Sentinel AI

## Quick Start (Local Server)

### 1. Prepare Environment

```bash
cd sentinel-ai
cp .env.example .env
# Edit .env:
#   GH_APP_ID=12345
#   GH_WEBHOOK_SECRET=your_secret
#   OPENROUTER_API_KEY=sk-or-... (optional but recommended)
```

### 2. Create GitHub App

Get your HTTPS webhook URL first:

- **Option A: Cloudflare Tunnel (free, no domain needed)**
  ```bash
  cloudflared tunnel login
  cloudflared tunnel create sentinel-ai
  cloudflared tunnel route dns sentinel-ai sentinel-ai
  # Then run: cloudflared tunnel run sentinel-ai
  # It will give you a URL like https://sentinel-ai.<random>.trycloudflare.com
  ```

- **Option B: ngrok**
  ```bash
  ngrok http 80  # because nginx proxies to Sentinel
  # Output: Forwarding https://<random>.ngrok.io -> http://localhost:80
  ```

- **Option C: Custom domain + certbot**
  ```bash
  # Point your domain A record to 207.180.223.192
  certbot --nginx -d yourdomain.com
  ```

Take the HTTPS URL (e.g., `https://sentinel-ai.trycloudflare.com`) and prepend `/webhook`. That's your webhook URL.

Now run the manifest generator:

```bash
python3 scripts/generate_github_app_manifest.py https://your-webhook-url/webhook
```

Copy the JSON and go to GitHub → Settings → Developer settings → GitHub Apps → New GitHub App → "Import an app manifest". Paste JSON.

After creating:
- Download the private key → save as `sentinel-ai/secrets/gh_private_key.pem`
- Note the **App ID** → put in `.env` as `GH_APP_ID`
- Note the **Webhook secret** → put in `.env` as `GH_WEBHOOK_SECRET`

### 3. Deploy

```bash
cd sentinel-ai
./deploy.sh
```

This will:
- Check `.env` and private key
- Start Docker Compose stack (API + dashboard)
- Print status

### 4. Install the App

Install the GitHub App on a test repository (or your whole account).

### 5. Test

Open a pull request in the test repo with some Python code containing:
- SQL string concatenation
- `os.system()` with variables
- Hardcoded passwords

Within 60 seconds, Sentinel will post a review comment with findings and suggestions.

### 6. Dashboard

Open your HTTPS URL (e.g., Cloudflare/ngrok domain) to see the Streamlit dashboard.

## Production Checklist

- [ ] Use a persistent domain (not ngrok) with Let's Encrypt cert
- [ ] Store secrets securely (use Docker secrets or environment file with restricted perms)
- [ ] Enable and configure PostgreSQL (`DATABASE_URL=postgresql://...`)
- [ ] Set up Redis for caching
- [ ] Configure log rotation (JSON logs to file)
- [ ] Add monitoring (Prometheus metrics endpoint already exists)
- [ ] Set up alerts for webhook failures
- [ ] Rate limiting per repo (future)
- [ ] Multi-tenant settings (future)

## Troubleshooting

| Symptom | Fix |
|---------|-----|
| 401 Invalid signature | GH_WEBHOOK_SECRET mismatch; regenerate |
| No review posted | Check Docker logs: `docker compose logs web` |
| LLM not working | Verify OPENROUTER_API_KEY and credits |
| Bandit/flake8 errors | They're preinstalled in Docker; if running outside, `pip install bandit flake8` |
| Webhook not delivered | Ensure HTTPS URL is correct and reachable (curl <url>/webhook) |
| 502 Bad Gateway from nginx | Docker containers not running: `docker compose ps` |

## Manual Test

```bash
curl -X POST https://your-domain.com/webhook \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: sha256=$(echo -n 'payload' | openssl sha256 -hmac 'your_secret' | cut -d' ' -f2)" \
  -d '{"action":"opened","repository":{"owner":{"login":"you"},"name":"test"},"pull_request":{"number":1,"head":{"sha":"abc"}}}'
```

Should return `202 {"status":"processing"}`.

---

**That's it. Sentinel AI is ready to secure your PRs.**
