#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

JAR_PATH="target/waimai-compare-1.0.0-SNAPSHOT.jar"
LOG_PATH="${SCRIPT_DIR}/waimai-compare.log"
AREX_AGENT_JAR_PATH="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-/home/test/arex-agent/arex-agent.jar}}"
AREX_STORAGE_URL="${AREX_STORAGE_URL:-127.0.0.1:8000}"

validate_arex_agent() {
  if [ ! -f "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar not found: $AREX_AGENT_JAR_PATH" >&2
    exit 1
  fi
  if [ ! -s "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar is empty: $AREX_AGENT_JAR_PATH" >&2
    exit 1
  fi
  if command -v jar >/dev/null 2>&1 && ! jar tf "$AREX_AGENT_JAR_PATH" >/dev/null 2>&1; then
    echo "ERROR: AREX agent jar is invalid or unreadable: $AREX_AGENT_JAR_PATH" >&2
    exit 1
  fi
}

if [ ! -f "$JAR_PATH" ]; then
  echo "Building..."
  cd "${SCRIPT_DIR}/.."
  mvn package -DskipTests -q
  cd "$SCRIPT_DIR"
fi

validate_arex_agent

echo "Starting waimai-compare on port 19092..."
setsid nohup java \
  -javaagent:"$AREX_AGENT_JAR_PATH" \
  -Darex.service.name=waimai-compare \
  -Darex.storage.service.host="$AREX_STORAGE_URL" \
  -Darex.record.rate=100 \
  ${JAVA_OPTS:--Xms256m -Xmx512m} \
  -jar "$JAR_PATH" \
  --server.port=19092 \
  > "$LOG_PATH" 2>&1 < /dev/null &
echo "PID: $!"
