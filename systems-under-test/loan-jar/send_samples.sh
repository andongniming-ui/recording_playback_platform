#!/usr/bin/env bash
set -euo pipefail

SERVER_PORT="${LOAN_SERVER_PORT:-4623}"
BASE_URL="${LOAN_BASE_URL:-http://127.0.0.1:${SERVER_PORT}}"
INTERVAL_SECONDS="${LOAN_SAMPLE_INTERVAL:-2}"

if [ "$#" -eq 0 ]; then
  set -- \
    "110101199001011234" \
    "310101198805201111" \
    "440101199509092222"
fi

first=1
for idcard in "$@"; do
  if [ "$first" -eq 0 ] && [ "$INTERVAL_SECONDS" != "0" ]; then
    sleep "$INTERVAL_SECONDS"
  fi
  first=0

  echo "GET ${BASE_URL}/loan/query?code=RP54KH01&idcard=${idcard}"
  curl -sS --fail "${BASE_URL}/loan/query?code=RP54KH01&idcard=${idcard}"
  echo
done
