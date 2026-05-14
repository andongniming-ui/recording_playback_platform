#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
exec > /tmp/restart_output.txt 2>&1

# Kill old vite process
pkill -f "vite" 2>/dev/null || true
sleep 1

# Start frontend
cd "${FRONTEND_DIR}"
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Wait for it to be ready
sleep 8

# Check if it's up
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
echo "Frontend HTTP status: $HTTP_CODE"

# Test login with form data
echo "=== Login test (form) ==="
curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin&password=admin123"
echo ""

echo "=== Chromium check ==="
python3 -c "
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    print('chromium ok')
    browser.close()
" 2>&1

echo "DONE"
