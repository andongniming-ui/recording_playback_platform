#!/bin/bash
exec > /tmp/check_env_output.txt 2>&1

echo "=== Browser check ==="
python3 -m playwright install chromium 2>&1 | tail -3

echo "=== Backend process ==="
ps aux | grep uvicorn | grep -v grep

echo "=== Frontend process ==="
ps aux | grep vite | grep -v grep

echo "=== Backend API test ==="
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'
echo ""

echo "=== Frontend accessible ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/

echo ""
echo "DONE"
