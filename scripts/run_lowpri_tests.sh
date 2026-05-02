#!/bin/bash
exec > /tmp/lowpri_test.log 2>&1

if ! curl -s -o /dev/null -w "%{http_code}" http://localhost:5173/ 2>/dev/null | grep -q "200"; then
    cd /home/recording_playback_platform/platform/frontend
    pkill -f vite 2>/dev/null; sleep 1
    nohup npm run dev -- --host 0.0.0.0 --port 5173 > /tmp/frontend_lowpri.log 2>&1 &
    sleep 12
fi
echo "Frontend: $(curl -s -o /dev/null -w '%{http_code}' http://localhost:5173/)"

rm -rf /tmp/lowpri_screenshots && mkdir -p /tmp/lowpri_screenshots
cd /home/recording_playback_platform
python3 tests/test_lowpri.py
echo "DONE"
