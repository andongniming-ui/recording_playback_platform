#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
exec > /tmp/test_run2.log 2>&1

echo "=== 检查服务 ==="
# 确保前端运行
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ 2>/dev/null | grep -q "200"; then
    echo "重启前端..."
    pkill -f vite 2>/dev/null; sleep 1
    cd "${FRONTEND_DIR}"
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend3.log 2>&1 &
    sleep 10
fi

# 确保后端运行
if ! curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "重启后端..."
    pkill -f uvicorn 2>/dev/null; sleep 1
    cd "${BACKEND_DIR}"
    nohup python3 -m uvicorn main:app --host 0.0.0.0 --port 8000 > /tmp/backend3.log 2>&1 &
    sleep 6
fi

FRONTEND=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/)
echo "Frontend status: $FRONTEND"
echo "Backend status: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/)"

echo "=== 清理旧截图 ==="
rm -rf /tmp/test_screenshots && mkdir -p /tmp/test_screenshots

echo "=== 运行测试 ==="
cd "${PROJECT_ROOT}"
python3 tests/test_frontend.py

echo "DONE at $(date)"
