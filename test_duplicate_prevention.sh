#!/bin/bash

RAILWAY_URL="https://web-production-98510.up.railway.app"

echo "🧪 Testing Duplicate Prevention on Railway"
echo "=============================================="
echo ""

# Test 1: Try to generate a post on a topic that already exists (quantum computing)
echo "Test 1: Attempting to generate 'quantum computing' (should be skipped as duplicate)"
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword":"quantum computing explained"}' \
  -s > /tmp/test1.json

echo "Result:"
cat /tmp/test1.json | jq '{success, message}'
echo ""

# Test 2: Try another existing topic (intermittent fasting)
echo "Test 2: Attempting to generate 'intermittent fasting' (should be skipped as duplicate)"
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword":"intermittent fasting benefits"}' \
  -s > /tmp/test2.json

echo "Result:"
cat /tmp/test2.json | jq '{success, message}'
echo ""

# Test 3: Try a genuinely new topic
echo "Test 3: Generating new unique topic 'machine learning for healthcare'"
curl -X POST "$RAILWAY_URL/api/generate-blog" \
  -H "Content-Type: application/json" \
  -d '{"keyword":"machine learning applications in modern healthcare"}' \
  -s > /tmp/test3.json

echo "Result:"
cat /tmp/test3.json | jq '{success, message, post: {title: .post.title, word_count: .post.word_count}}'
echo ""

echo "=============================================="
echo "✅ Duplicate prevention test complete!"
