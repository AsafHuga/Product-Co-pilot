#!/bin/bash

echo "Testing Railway API Deployment..."
echo ""

echo "1. Testing health endpoint..."
curl -s https://web-production-55d55.up.railway.app/ | python3 -m json.tool
echo ""

echo "2. Testing file upload and analysis..."
curl -X POST "https://web-production-55d55.up.railway.app/analyze/quick" \
  -F "file=@/Users/asafhuga/Desktop/sample_timeseries.csv" \
  -s -w "\nHTTP Status: %{http_code}\n" | head -50

echo ""
echo "✅ Tests complete!"
