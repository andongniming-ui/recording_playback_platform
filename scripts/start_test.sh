#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
# Start backend
cd "${BACKEND_DIR}"
nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 8
echo "=== Backend log ==="
tail -30 /tmp/backend.log

# Test backend
echo "=== Backend health ==="
curl -s http://localhost:8000/api/health
