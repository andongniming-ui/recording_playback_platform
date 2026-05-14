#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
exec > /tmp/check_and_test.log 2>&1

echo "=== 检查进程 ==="
ps aux | grep -E "uvicorn|vite|node" | grep -v grep || true

echo "=== 检查端口 ==="
ss -tlnp | grep -E "5173|8000" || true

echo "=== 重启前端(如需) ==="
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ | grep -q "200"; then
    echo "前端未运行，重启..."
    pkill -f vite 2>/dev/null || true
    sleep 1
    cd "${FRONTEND_DIR}"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend2.log 2>&1 &
    echo "Frontend PID: $!"
    sleep 10
    HTTP=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
    echo "Frontend HTTP: $HTTP"
else
    echo "前端已运行"
fi

echo "=== 重启后端(如需) ==="
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200\|404\|422"; then
    echo "后端未运行，重启..."
    pkill -f uvicorn 2>/dev/null || true
    sleep 1
    cd "${BACKEND_DIR}"
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend2.log 2>&1 &
    echo "Backend PID: $!"
    sleep 6
fi

echo "=== 运行测试 ==="
cd "${PROJECT_ROOT}"
python3 tests/test_frontend.py

echo "=== 完成 ==="
