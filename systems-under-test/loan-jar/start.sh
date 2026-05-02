#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

JAR_PATH="${LOAN_JAR_PATH:-$SCRIPT_DIR/loan.jar}"
SERVER_PORT="${LOAN_SERVER_PORT:-4623}"
SERVICE_NAME="${AREX_SERVICE_NAME:-loan-jar}"

DB_HOST="${LOAN_DB_HOST:-127.0.0.1}"
DB_PORT="${LOAN_DB_PORT:-3307}"
DB_NAME="${LOAN_DB_NAME:-loan_jar}"
DB_USERNAME="${LOAN_DB_USERNAME:-root}"
DB_PASSWORD="${LOAN_DB_PASSWORD:-root123}"
DB_URL="${LOAN_DB_URL:-jdbc:mysql://${DB_HOST}:${DB_PORT}/${DB_NAME}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true}"

LOAN_ENABLE_AREX="${LOAN_ENABLE_AREX:-1}"
AREX_AGENT_JAR_PATH="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-/home/test/arex-agent/arex-agent.jar}}"
AREX_STORAGE_URL="${AREX_STORAGE_URL:-127.0.0.1:8000}"
AREX_RECORD_RATE="${AREX_RECORD_RATE:-100}"
JAVA_OPTS="${JAVA_OPTS:--Xms256m -Xmx512m}"

validate_loan_jar() {
  if [ ! -f "$JAR_PATH" ]; then
    echo "ERROR: loan jar not found: $JAR_PATH" >&2
    exit 1
  fi

  if [ ! -s "$JAR_PATH" ]; then
    echo "ERROR: loan jar is empty: $JAR_PATH" >&2
    exit 1
  fi
}

validate_arex_agent() {
  if [ ! -f "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar not found: $AREX_AGENT_JAR_PATH" >&2
    echo "Set AREX_AGENT_JAR_PATH, or start with LOAN_ENABLE_AREX=0 for local smoke testing." >&2
    exit 1
  fi

  if [ ! -s "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar is empty: $AREX_AGENT_JAR_PATH" >&2
    echo "Restore the agent jar, or start with LOAN_ENABLE_AREX=0 for local smoke testing." >&2
    exit 1
  fi

  if command -v jar >/dev/null 2>&1 && ! jar tf "$AREX_AGENT_JAR_PATH" >/dev/null 2>&1; then
    echo "ERROR: AREX agent jar is invalid or unreadable: $AREX_AGENT_JAR_PATH" >&2
    exit 1
  fi
}

validate_loan_jar

AREX_ARGS=()
case "$LOAN_ENABLE_AREX" in
  0|false|FALSE|no|NO)
    echo "Starting loan-jar without AREX agent on port ${SERVER_PORT}..."
    ;;
  *)
    validate_arex_agent
    echo "Starting loan-jar with AREX agent on port ${SERVER_PORT}, service name ${SERVICE_NAME}..."
    AREX_ARGS=(
      "-javaagent:${AREX_AGENT_JAR_PATH}"
      "-Darex.service.name=${SERVICE_NAME}"
      "-Darex.storage.service.host=${AREX_STORAGE_URL}"
      "-Darex.record.rate=${AREX_RECORD_RATE}"
    )
    ;;
esac

# shellcheck disable=SC2086
exec java \
  "${AREX_ARGS[@]}" \
  ${JAVA_OPTS} \
  -jar "$JAR_PATH" \
  --server.port="$SERVER_PORT" \
  --spring.datasource.url="$DB_URL" \
  --spring.datasource.username="$DB_USERNAME" \
  --spring.datasource.password="$DB_PASSWORD"
