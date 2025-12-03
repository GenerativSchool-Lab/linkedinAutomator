#!/bin/bash

# API Endpoint Testing Script
BASE_URL="https://backend-production-433a.up.railway.app"

echo "🧪 Testing LinkedIn Prospection Agent API"
echo "=========================================="
echo ""

echo "1. Health Check:"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""

echo "2. API Root:"
curl -s "$BASE_URL/" | python3 -m json.tool
echo ""

echo "3. Stats Endpoint:"
curl -s "$BASE_URL/api/stats" | python3 -m json.tool
echo ""

echo "4. Profiles Endpoint:"
curl -s "$BASE_URL/api/profiles" | python3 -m json.tool
echo ""

echo "5. Connections Endpoint:"
curl -s "$BASE_URL/api/connections" | python3 -m json.tool
echo ""

echo "6. Messages Endpoint:"
curl -s "$BASE_URL/api/messages" | python3 -m json.tool 2>&1 || curl -s "$BASE_URL/api/messages"
echo ""

echo "✅ API Testing Complete!"

