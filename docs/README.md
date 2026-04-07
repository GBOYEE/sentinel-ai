# Sentinel AI — Quickstart

## 5-Minute Setup

### 1. Create a GitHub App

1. Go to GitHub → Settings → Developer settings → GitHub Apps → New GitHub App
2. Fill in:
   - **GitHub App name:** Sentinel AI
   - **Webhook URL:** `https://your-domain.com/webhook` (use ngrok for local)
   - **Repository permissions:**
     - Pull requests: Read & Write
     - Contents: Read
     - Metadata: Read
   - **Subscribe to events:** Pull request
3. Generate a private key and download it
4. Note the **App ID** and **Webhook secret**

### 2. Deploy Sentinel

```bash
git clone https://github.com/GBOYEE/sentinel-ai.git
cd sentinel-ai
cp .env.example .env
# Edit .env with your GH_APP_ID, GH_WEBHOOK_SECRET, and ensure GH_APP_PRIVATE_KEY path points to secrets/gh_private_key.pem
docker compose up -d
```

### 3. Install the App on Your Repo

- After creating the GitHub App, install it on the target repository(s)
- Alternatively use the installation URL provided by GitHub

### 4. Test

Open a pull request in the monitored repository. Sentinel will post a review comment within a minute.

## Manual Testing

```bash
# Trigger a test review (simulate webhook)
curl -X POST http://localhost:8000/webhook \
  -H "X-GitHub-Event: pull_request" \
  -H "X-Hub-Signature-256: <test-signature>" \
  -d '{"action":"opened","repository":{"owner":{"login":"you"},"name":"test"},"pull_request":{"number":1,"head":{"sha":"abc123"}}}'
```

## Dashboard

Open http://localhost:8501 to see the Streamlit dashboard with review history and metrics.

## Development

```bash
pip install -r requirements.txt
uvicorn sentinel_ai.main:app --reload
streamlit run dashboard.py
```
