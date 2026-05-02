#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

JAR_PATH="${CREDIT_JAR_PATH:-$SCRIPT_DIR/credit.jar}"
SERVER_PORT="${CREDIT_SERVER_PORT:-8623}"
SERVICE_NAME="${AREX_SERVICE_NAME:-credit-jar}"

DB_HOST="${CREDIT_DB_HOST:-127.0.0.1}"
DB_PORT="${CREDIT_DB_PORT:-3307}"
DB_USERNAME="${CREDIT_DB_USERNAME:-root}"
DB_PASSWORD="${CREDIT_DB_PASSWORD:-root123}"

CREDIT_DB_NAME="${CREDIT_DB_NAME:-credit}"
ORDER_DB_NAME="${ORDER_DB_NAME:-order}"

CREDIT_DB_URL="jdbc:mysql://${DB_HOST}:${DB_PORT}/${CREDIT_DB_NAME}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true"
ORDER_DB_URL="jdbc:mysql://${DB_HOST}:${DB_PORT}/${ORDER_DB_NAME}?useUnicode=true&characterEncoding=utf8&serverTimezone=Asia/Shanghai&useSSL=false&allowPublicKeyRetrieval=true"

CREDIT_ENABLE_AREX="${CREDIT_ENABLE_AREX:-1}"
AREX_AGENT_JAR_PATH="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-/home/test/arex-agent/arex-agent.jar}}"
AREX_STORAGE_URL="${AREX_STORAGE_URL:-127.0.0.1:8000}"
AREX_RECORD_RATE="${AREX_RECORD_RATE:-100}"
JAVA_OPTS="${JAVA_OPTS:--Xms256m -Xmx512m}"

validate_credit_jar() {
  if [ ! -f "$JAR_PATH" ]; then
    echo "ERROR: credit jar not found: $JAR_PATH" >&2
    exit 1
  fi
  if [ ! -s "$JAR_PATH" ]; then
    echo "ERROR: credit jar is empty: $JAR_PATH" >&2
    exit 1
  fi
}

validate_arex_agent() {
  if [ ! -f "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar not found: $AREX_AGENT_JAR_PATH" >&2
    echo "Set AREX_AGENT_JAR_PATH, or start with CREDIT_ENABLE_AREX=0 for local smoke testing." >&2
    exit 1
  fi
  if [ ! -s "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar is empty: $AREX_AGENT_JAR_PATH" >&2
    exit 1
  fi
}

validate_credit_jar

AREX_ARGS=()
case "$CREDIT_ENABLE_AREX" in
  0|false|FALSE|no|NO)
    echo "Starting credit-jar without AREX agent on port ${SERVER_PORT}..."
    ;;
  *)
    validate_arex_agent
    echo "Starting credit-jar with AREX agent on port ${SERVER_PORT}, service name ${SERVICE_NAME}..."
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
  --server.port="${SERVER_PORT}" \
  --spring.datasource.dynamic.datasource.credit.url="${CREDIT_DB_URL}" \
  --spring.datasource.dynamic.datasource.credit.username="${DB_USERNAME}" \
  --spring.datasource.dynamic.datasource.credit.password="${DB_PASSWORD}" \
  --spring.datasource.dynamic.datasource.order.url="${ORDER_DB_URL}" \
  --spring.datasource.dynamic.datasource.order.username="${DB_USERNAME}" \
  --spring.datasource.dynamic.datasource.order.password="${DB_PASSWORD}"
