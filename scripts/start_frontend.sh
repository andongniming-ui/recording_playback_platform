#!/bin/bash
cd /home/recording_playback_platform/platform/frontend
nohup npm run dev -- --host 0.0.0.0 > /tmp/frontend.log 2>&1 &
echo "Frontend PID: $!"
sleep 10
echo "=== Frontend log ==="
tail -20 /tmp/frontend.log
