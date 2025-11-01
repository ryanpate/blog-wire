#!/bin/bash

echo "🚂 Blog Wire - Railway Deployment Script"
echo "=========================================="
echo ""

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found"
    echo "Install with: npm install -g @railway/cli"
    exit 1
fi

echo "✅ Railway CLI found"
echo ""

# Check if logged in
echo "Checking Railway authentication..."
railway whoami &> /dev/null

if [ $? -ne 0 ]; then
    echo "❌ Not logged in to Railway"
    echo ""
    echo "Please run manually in your terminal:"
    echo "  railway login"
    echo ""
    echo "Then run this script again."
    exit 1
fi

echo "✅ Logged in to Railway"
echo ""

# Check if OPENAI_API_KEY is set locally
if [ -f .env ]; then
    source .env
    if [ -z "$OPENAI_API_KEY" ] || [ "$OPENAI_API_KEY" = "your_openai_api_key_here" ]; then
        echo "⚠️  Warning: OPENAI_API_KEY not configured in .env"
        echo "Make sure to set it in Railway after deployment"
    fi
fi

# Initialize or link project
echo "Step 1: Initialize Railway Project"
echo "-----------------------------------"
railway whoami

echo ""
echo "Choose an option:"
echo "  1) Create NEW Railway project"
echo "  2) Link to EXISTING Railway project"
echo ""
read -p "Enter choice (1 or 2): " choice

if [ "$choice" = "1" ]; then
    echo ""
    echo "Creating new Railway project..."
    railway init
elif [ "$choice" = "2" ]; then
    echo ""
    echo "Linking to existing project..."
    railway link
else
    echo "Invalid choice. Exiting."
    exit 1
fi

echo ""
echo "Step 2: Set Environment Variables"
echo "-----------------------------------"

# Generate SECRET_KEY
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

echo "Setting SECRET_KEY..."
railway variables set SECRET_KEY="$SECRET_KEY"

echo ""
echo "⚠️  IMPORTANT: You need to set OPENAI_API_KEY manually"
echo ""
echo "Run this command with YOUR API key:"
echo "  railway variables set OPENAI_API_KEY=sk-your-actual-key-here"
echo ""
read -p "Press Enter after you've set OPENAI_API_KEY..."

echo ""
echo "Setting other variables..."
railway variables set FLASK_ENV=production
railway variables set BLOG_NAME="Blog Wire"
railway variables set POSTS_PER_DAY=1
railway variables set MIN_WORD_COUNT=2000
railway variables set MAX_WORD_COUNT=3500

echo ""
echo "Step 3: Deploy to Railway"
echo "-----------------------------------"
echo "Deploying your application..."
echo ""

railway up

echo ""
echo "=========================================="
echo "🎉 Deployment Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Check deployment status: railway status"
echo "  2. View logs: railway logs"
echo "  3. Open in browser: railway open"
echo "  4. Get URL: railway status"
echo ""
echo "To add daily automation (scheduler):"
echo "  - Go to Railway dashboard"
echo "  - Add a Cron Job service"
echo "  - Schedule: 0 8 * * * (8 AM daily)"
echo "  - Command: python scheduler.py"
echo ""
echo "Documentation: RAILWAY_DEPLOYMENT.md"
echo ""
