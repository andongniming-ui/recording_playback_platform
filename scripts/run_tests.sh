#!/usr/bin/env bash
set -euo pipefail
. "$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/lib/project.sh"
exec > /tmp/test_run.log 2>&1
echo "Starting frontend tests at $(date)"
cd "${PROJECT_ROOT}"
python3 tests/test_frontend.py
echo "Tests finished at $(date)"
echo "EXIT_CODE: $?"
