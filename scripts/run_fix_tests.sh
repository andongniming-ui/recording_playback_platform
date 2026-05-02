#!/bin/bash
exec > /tmp/fix_test.log 2>&1

# 确保前端在运行
if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ 2>/dev/null | grep -q "200"; then
    cd /home/recording_playback_platform/platform/frontend
    pkill -f vite 2>/dev/null; sleep 1
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend_fix.log 2>&1 &
    sleep 10
fi
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/)"

rm -rf /tmp/fix_screenshots && mkdir -p /tmp/fix_screenshots
cd /home/recording_playback_platform
python3 tests/test_fixes.py
echo "DONE"
