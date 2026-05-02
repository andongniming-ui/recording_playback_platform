#!/usr/bin/env bash
set -euo pipefail

BASE_URL="http://127.0.0.1:18081"
DURATION_SECONDS=0
INTERVAL_SECONDS=30
TIMEOUT_SECONDS=10
CODES=""
STOP_ON_ERROR=0
DRY_RUN=0

usage() {
  cat <<'EOF'
Usage:
  ./run_long_recording.sh [options]

Options:
  --base-url URL       Target didi system URL. Default: http://127.0.0.1:18081
  --duration SECONDS   Run duration. 0 means run until Ctrl+C. Default: 0
  --interval SECONDS   Sleep interval between requests. Default: 30
  --timeout SECONDS    curl max time per request. Default: 10
  --codes LIST         Comma separated transaction codes. Default: car000001..car000030
                       Example: car000001,car000007,car000012
  --stop-on-error      Exit immediately when one request fails.
  --dry-run            Print generated requests without sending them.
  -h, --help           Show this help.

Examples:
  # Keep sending to SAT didi-system-a until Ctrl+C.
  ./run_long_recording.sh

  # Run for one week, one request every 60 seconds.
  ./run_long_recording.sh --duration 604800 --interval 60

  # Only hit several complex transactions that include HTTP sub-calls and DB calls.
  ./run_long_recording.sh --codes car000001,car000007,car000008,car000012,car000013 --interval 3
EOF
}

build_field_name() {
  case "$1" in
    car000001|car000002|car000003|car000004|car000005|car000016|car000017|car000018|car000019|car000020)
      echo "code"
      ;;
    car000006|car000007|car000008|car000009|car000010|car000021|car000022|car000023|car000024|car000025)
      echo "trs_code"
      ;;
    car000011|car000012|car000013|car000026|car000027|car000028)
      echo "service_code"
      ;;
    *)
      echo "biz_code"
      ;;
  esac
}

default_codes() {
  local i
  for i in $(seq 1 30); do
    printf "car%06d\n" "$i"
  done
}

parse_codes() {
  if [[ -z "$CODES" ]]; then
    default_codes
    return
  fi
  tr ',' '\n' <<< "$CODES" | sed '/^[[:space:]]*$/d'
}

build_xml() {
  local code="$1"
  local request_no="$2"
  local field
  field="$(build_field_name "$code")"
  cat <<EOF
<request>
  <${field}>${code}</${field}>
  <request_no>${request_no}</request_no>
  <customer_no>C10001</customer_no>
  <plate_no>沪A10001</plate_no>
  <vin>VIN0000000000000001</vin>
  <policy_no>P10001</policy_no>
  <claim_no>CL10001</claim_no>
  <garage_code>G001</garage_code>
  <city>SHANGHAI</city>
</request>
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --base-url)
      BASE_URL="${2:?missing --base-url value}"
      shift 2
      ;;
    --duration)
      DURATION_SECONDS="${2:?missing --duration value}"
      shift 2
      ;;
    --interval)
      INTERVAL_SECONDS="${2:?missing --interval value}"
      shift 2
      ;;
    --timeout)
      TIMEOUT_SECONDS="${2:?missing --timeout value}"
      shift 2
      ;;
    --codes)
      CODES="${2:?missing --codes value}"
      shift 2
      ;;
    --stop-on-error)
      STOP_ON_ERROR=1
      shift
      ;;
    --dry-run)
      DRY_RUN=1
      shift
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
done

ENDPOINT="${BASE_URL%/}/api/car/service"
mapfile -t CODE_LIST < <(parse_codes)
if [[ ${#CODE_LIST[@]} -eq 0 ]]; then
  echo "No transaction code configured." >&2
  exit 2
fi

START_EPOCH="$(date +%s)"
RUN_ID="$(date +%Y%m%d%H%M%S)"
TOTAL=0
OK=0
FAIL=0

echo "Target: ${ENDPOINT}"
echo "Duration: ${DURATION_SECONDS}s (0 means until Ctrl+C), interval: ${INTERVAL_SECONDS}s, codes: ${#CODE_LIST[@]}"
echo "Run id: ${RUN_ID}"
echo "Press Ctrl+C to stop."

while true; do
  now="$(date +%s)"
  if [[ "$DURATION_SECONDS" -gt 0 && $((now - START_EPOCH)) -ge "$DURATION_SECONDS" ]]; then
    break
  fi

  for code in "${CODE_LIST[@]}"; do
    now="$(date +%s)"
    if [[ "$DURATION_SECONDS" -gt 0 && $((now - START_EPOCH)) -ge "$DURATION_SECONDS" ]]; then
      break 2
    fi

    TOTAL=$((TOTAL + 1))
    request_no="REQ-${code}-${RUN_ID}-${TOTAL}"
    xml="$(build_xml "$code" "$request_no")"

    if [[ "$DRY_RUN" -eq 1 ]]; then
      printf '[%s] DRY %s %s\n' "$(date '+%F %T')" "$code" "$request_no"
      printf '%s\n' "$xml"
    else
      http_code="$(
        curl -sS -o /tmp/didi-long-recording-response.txt \
          -w '%{http_code}' \
          --max-time "$TIMEOUT_SECONDS" \
          -H 'Content-Type: application/xml' \
          -d "$xml" \
          "$ENDPOINT" || true
      )"

      if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
        OK=$((OK + 1))
        printf '[%s] OK   code=%s request_no=%s http=%s total=%d ok=%d fail=%d\n' \
          "$(date '+%F %T')" "$code" "$request_no" "$http_code" "$TOTAL" "$OK" "$FAIL"
      else
        FAIL=$((FAIL + 1))
        printf '[%s] FAIL code=%s request_no=%s http=%s total=%d ok=%d fail=%d\n' \
          "$(date '+%F %T')" "$code" "$request_no" "${http_code:-curl_error}" "$TOTAL" "$OK" "$FAIL" >&2
        sed -n '1,6p' /tmp/didi-long-recording-response.txt >&2 || true
        if [[ "$STOP_ON_ERROR" -eq 1 ]]; then
          exit 1
        fi
      fi
    fi

    sleep "$INTERVAL_SECONDS"
  done
done

echo "Finished. total=${TOTAL}, ok=${OK}, fail=${FAIL}"
