# GitHub App Setup Guide for Sentinel AI

## Step 1: Create the GitHub App

1. Go to https://github.com/settings/apps/new
2. Fill in:
   - **GitHub App name**: `Sentinel AI`
   - **Description**: `AI-powered PR security and quality reviewer. Combines static analysis (bandit, flake8, semgrep) with LLM reasoning to catch vulnerabilities and quality issues on every PR.`
   - **Homepage URL**: `https://github.com/GBOYEE/sentinel-ai`
   - **Webhook URL**: `http://YOUR_SERVER_IP:8000/webhook` (update after deployment)
   - **Webhook secret**: Generate a strong random string (save it!)
   - **Setup URL**: `https://github.com/GBOYEE/sentinel-ai`

3. Permissions:
   - **Repository permissions**:
     - Contents: Read-only
     - Pull requests: Read & write
     - Metadata: Read-only
   - **Subscribe to events**:
     - Pull request
     - Installation
     - Installation repositories

4. **Where can this GitHub App be installed?** Any account

5. Click **Create GitHub App**

## Step 2: Generate Private Key

1. In the app settings, scroll to **Private keys**
2. Click **Generate a private key**
3. Save the `.pem` file to your server at `/root/github-dev/projects/sentinel-ai/secrets/gh_private_key.pem`

## Step 3: Note the App ID

Copy the **App ID** from the app settings page.

## Step 4: Configure Environment

```bash
cd /root/github-dev/projects/sentinel-ai
cp .env.example .env

# Edit .env:
GH_APP_ID=<your-app-id>
GH_APP_PRIVATE_KEY=./secrets/gh_private_key.pem
GH_WEBHOOK_SECRET=<your-webhook-secret>
OPENROUTER_API_KEY=<your-openrouter-key>
```

## Step 5: Deploy

```bash
# Using Docker
docker-compose up -d

# Or directly
source .venv/bin/activate
uvicorn sentinel_ai.main:app --host 0.0.0.0 --port 8000
```

## Step 6: Install the App

1. Go to the app's page: https://github.com/apps/sentinel-ai
2. Click **Install**
3. Select repositories
4. Open a test PR — Sentinel AI will review it!

## Step 7: Publish to Marketplace

1. Go to https://github.com/marketplace/new
2. Select your app
3. Fill in listing details (use README content)
4. Set pricing: Free / $9/mo / $29/mo
5. Submit for review
