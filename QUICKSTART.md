# Sentinel AI — Quick Checklist

## Prerequisites
- [ ] Cloudflare Tunnel or ngrok running (HTTPS URL)
- [ ] GitHub App created (App ID, Webhook secret, private key)

## Setup Steps

### 1. Prepare Environment
```bash
cd sentinel-ai
cp .env.example .env
# Edit .env with your values
mkdir -p secrets
```

### 2. Save GitHub App Private Key
Place the `.pem` file at: `secrets/gh_private_key.pem`

### 3. Fill .env Variables
```
GH_APP_ID=12345
GH_WEBHOOK_SECRET=your_webhook_secret
OPENROUTER_API_KEY=sk-or-...  # optional but recommended for LLM review
```

### 4. Deploy
```bash
./deploy.sh
```

### 5. Install GitHub App
Go to your GitHub App → Install → select test repository

### 6. Test
Open a PR with vulnerable Python code. Should see review within 60s.

### 7. Dashboard
Visit your HTTPS URL (or http://localhost:8501 if local)

---

**Docs:** See DEPLOYMENT.md for full guide, troubleshooting, and production checklist.
