#!/bin/bash
exec > /tmp/test_run.log 2>&1
echo "Starting frontend tests at $(date)"
cd /home/recording_playback_platform
python3 tests/test_frontend.py
echo "Tests finished at $(date)"
echo "EXIT_CODE: $?"
