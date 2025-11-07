#!/bin/bash

# Generate 9 diverse blog posts on Railway via API
RAILWAY_URL="https://web-production-98510.up.railway.app"

echo "🚀 Generating 9 diverse blog posts on Railway..."
echo "=============================================="

# Topic 1: Quantum Computing
echo ""
echo "[1/9] Generating: Quantum Computing for Beginners..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "quantum computing explained for beginners"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 2: Intermittent Fasting
echo ""
echo "[2/9] Generating: Intermittent Fasting Benefits..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "intermittent fasting benefits and how to start"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 3: Passive Income
echo ""
echo "[3/9] Generating: Passive Income Strategies..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "passive income strategies for 2025"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 4: Minimalist Living
echo ""
echo "[4/9] Generating: Minimalist Living Tips..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "minimalist living tips for reducing stress"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 5: Digital Marketing
echo ""
echo "[5/9] Generating: Digital Marketing Strategies..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "digital marketing strategies for small businesses"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 6: Budget Travel
echo ""
echo "[6/9] Generating: Budget Travel in Europe..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "budget travel destinations in Europe"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 7: Meal Prep
echo ""
echo "[7/9] Generating: Healthy Meal Prep Ideas..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "healthy meal prep ideas for busy professionals"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 8: Productivity Apps
echo ""
echo "[8/9] Generating: Productivity Apps for Remote Workers..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "productivity apps and tools for remote workers"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

sleep 5

# Topic 9: Sustainable Fashion
echo ""
echo "[9/9] Generating: Sustainable Fashion Trends..."
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword": "sustainable fashion trends and eco-friendly brands"}' \
  -s | jq -r '.message // .post.title' || echo "Failed"

echo ""
echo "=============================================="
echo "✅ Done! Check your blog at: $RAILWAY_URL"
echo ""
echo "View stats:"
curl -s "$RAILWAY_URL/api/stats" | jq '.'
