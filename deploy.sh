#!/bin/bash
# Sentinel AI — Production Deployment Script
# Run this after setting environment variables in .env

set -e

echo "🛡️  Deploying Sentinel AI..."

# Ensure .env exists and has required vars
if [ ! -f .env ]; then
    echo "❌ .env file not found. Copy .env.example and fill in values."
    exit 1
fi

# Create secrets directory if needed
mkdir -p secrets

# Check if private key exists
if [ ! -f secrets/gh_private_key.pem ]; then
    echo "⚠️  Private key not found at secrets/gh_private_key.pem"
    echo "   Place your GitHub App private key there before continuing."
    exit 1
fi

# Start Docker stack
echo "🐳 Starting Docker Compose stack..."
docker compose up -d

# Wait for services
echo "⏳ Waiting for services to be healthy..."
sleep 5

# Check API
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ API is running"
else
    echo "⚠️  API health check failed"
fi

# Check dashboard
if curl -s http://localhost:8501 > /dev/null 2>&1; then
    echo "✅ Dashboard is running"
else
    echo "⚠️  Dashboard not responding"
fi

echo ""
echo "🎯 NEXT STEPS:"
echo "1. Ensure your webhook URL (HTTPS) points to this server."
echo "   - Use Cloudflare Tunnel: cloudflared tunnel create sentinel-ai && cloudflared tunnel route dns sentinel-ai <subdomain>"
echo "   - Or ngrok: ngrok http 80"
echo "2. Create a GitHub App with the manifest, using your HTTPS webhook URL."
echo "3. Update .env with GH_APP_ID and GH_WEBHOOK_SECRET (already should be there)."
echo "4. Restart: docker compose restart web"
echo "5. Install the GitHub App on your target repositories."
echo "6. Open a PR and watch Sentinel review!"
echo ""
echo "📊 Dashboard: http://localhost:8501 (or via nginx proxy)"
echo "🔗 API health: http://localhost:8000/health"
