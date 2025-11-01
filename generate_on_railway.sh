#!/bin/bash

# Generate 5 trending blog posts on Railway via API
RAILWAY_URL="https://web-production-98510.up.railway.app"

echo "Generating 5 trending blog posts on Railway..."
echo "=============================================="

# Topic 1: AI for Business
echo ""
echo "[1/5] Generating: AI for Business Growth in 2025..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "how to use artificial intelligence for business growth in 2025"}' \
  -s | jq -r '.message'

sleep 5

# Topic 2: Cryptocurrency Investing
echo ""
echo "[2/5] Generating: Cryptocurrency Investing for Beginners..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "best ways to invest in cryptocurrency for beginners step by step"}' \
  -s | jq -r '.message'

sleep 5

# Topic 3: Online Business
echo ""
echo "[3/5] Generating: Starting Online Business from Home..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "complete guide to starting a successful online business from home"}' \
  -s | jq -r '.message'

sleep 5

# Topic 4: Mental Health
echo ""
echo "[4/5] Generating: Mental Health and Stress Reduction..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "how to improve mental health and reduce stress naturally"}' \
  -s | jq -r '.message'

sleep 5

# Topic 5: Sustainable Living
echo ""
echo "[5/5] Generating: Sustainable Living Tips..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "sustainable living tips for reducing carbon footprint at home"}' \
  -s | jq -r '.message'

echo ""
echo "=============================================="
echo "Done! Check your blog at: $RAILWAY_URL"
