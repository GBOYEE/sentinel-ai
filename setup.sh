#!/bin/bash
# Sentinel AI — GitHub App Creation Helper
# Run this after creating the GitHub App via the web UI

set -e

echo "🛡️ Sentinel AI — GitHub App Setup"
echo "=================================="
echo ""

# Check if we're in the right directory
if [ ! -f "sentinel_ai/main.py" ]; then
    echo "❌ Run this from the sentinel-ai project root"
    exit 1
fi

# Step 1: Get App ID
echo "Step 1: GitHub App Credentials"
echo ""
echo "Go to https://github.com/settings/apps/new and create the app with these settings:"
echo ""
echo "  GitHub App name:     Sentinel AI"
echo "  Description:         AI-powered PR security and quality reviewer"
echo "  Homepage URL:        https://github.com/GBOYEE/sentinel-ai"
echo "  Webhook URL:         http://79.143.186.95:8000/webhook"
echo "  Setup URL:           https://github.com/GBOYEE/sentinel-ai"
echo ""
echo "  Permissions needed:"
echo "    - Contents: Read-only"
echo "    - Pull requests: Read & write"
echo "    - Metadata: Read-only"
echo ""
echo "  Events to subscribe to:"
echo "    - Pull request"
echo "    - Installation"
echo "    - Installation repositories"
echo ""
echo "  Where can this be installed?: Any account"
echo ""
read -p "Press Enter after creating the app..."

# Step 2: Get App ID
echo ""
read -p "Enter the App ID: " APP_ID

# Step 3: Generate private key
echo ""
echo "Step 2: Generate private key"
mkdir -p secrets
openssl genrsa -out secrets/gh_private_key.pem 2048 2>/dev/null
echo "✅ Private key generated at secrets/gh_private_key.pem"

# Step 4: Get webhook secret
echo ""
read -p "Enter the Webhook Secret: " WEBHOOK_SECRET

# Step 5: Get OpenRouter key
echo ""
read -p "Enter your OpenRouter API key (or press Enter to skip): " OPENROUTER_KEY

# Step 6: Update .env
echo ""
echo "Step 3: Updating .env"
cat > .env << ENVEOF
GH_APP_ID=${APP_ID}
GH_APP_PRIVATE_KEY=./secrets/gh_private_key.pem
GH_WEBHOOK_SECRET=${WEBHOOK_SECRET}
OPENROUTER_API_KEY=${OPENROUTER_KEY}
OPENROUTER_MODEL=openai/gpt-4o-mini
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_URL=sqlite:///./sentinel.db
CHROMA_PERSIST_DIR=./chroma_data
ENABLE_STATIC_ANALYSIS=true
ENABLE_LLM_REVIEW=true
SCAN_TIMEOUT=300
ENVEOF

echo "✅ .env updated"

# Step 7: Restart the app
echo ""
echo "Step 4: Restarting Sentinel AI"
pkill -f "uvicorn sentinel_ai" 2>/dev/null || true
sleep 1

source .venv/bin/activate
nohup uvicorn sentinel_ai.main:app --host 0.0.0.0 --port 8000 > /tmp/sentinel.log 2>&1 &
sleep 3

# Health check
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Sentinel AI is running on port 8000"
else
    echo "❌ Failed to start. Check /tmp/sentinel.log"
    exit 1
fi

echo ""
echo "=================================="
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Go to https://github.com/apps/sentinel-ai"
echo "  2. Click 'Install' and select your repos"
echo "  3. Open a test PR — Sentinel AI will review it"
echo "  4. Publish to Marketplace: https://github.com/marketplace/new"
echo ""
