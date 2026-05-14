#!/usr/bin/env bash
set -euo pipefail
python3 -c "from playwright.sync_api import sync_playwright; print('playwright ok')" 2>&1 || echo "playwright not installed"
python3 -m playwright --version 2>&1 || echo "playwright cli not found"
