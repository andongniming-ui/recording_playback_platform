#!/usr/bin/env bash
set -euo pipefail
echo "=== Browser check ==="
python3 -m playwright install chromium --with-deps 2>&1 | tail -5

echo "=== Backend API check ==="
curl -s http://localhost:8000/api/v1/applications/ 2>&1 | head -50
echo ""
echo "=== Login API ==="
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d 'username=admin&password=admin123' 2>&1 | head -100
