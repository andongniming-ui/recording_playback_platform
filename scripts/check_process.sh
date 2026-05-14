#!/usr/bin/env bash
set -euo pipefail
echo "=== python3 processes ==="
ps aux | grep python3 | grep -v grep || true
echo "=== frontend ==="
curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/
echo ""
echo "=== fix_test.log tail ==="
tail -20 /tmp/fix_test.log 2>/dev/null || echo "(empty)"
