#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
cd "${FRONTEND_DIR}"
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
echo "Frontend PID: $!"
sleep 10
echo "=== Frontend log ==="
tail -20 /tmp/frontend.log
