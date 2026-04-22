#!/usr/bin/env bash
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

JAR_PATH="target/didi-system-b-1.0.0.jar"
AREX_STORAGE_URL="${AREX_STORAGE_URL:-127.0.0.1:8000}"
AREX_AGENT_JAR_PATH="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-/home/test/arex-agent/arex-agent.jar}}"

validate_arex_agent() {
  if [ ! -f "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar not found: $AREX_AGENT_JAR_PATH" >&2
    echo "Set AREX_AGENT_JAR_PATH or AR_AREX_AGENT_JAR_PATH to a valid arex-agent.jar before starting didi-system-b." >&2
    exit 1
  fi

  if [ ! -s "$AREX_AGENT_JAR_PATH" ]; then
    echo "ERROR: AREX agent jar is empty: $AREX_AGENT_JAR_PATH" >&2
    echo "Restore the jar or point AREX_AGENT_JAR_PATH to a valid copy before starting didi-system-b." >&2
    exit 1
  fi

  if command -v jar >/dev/null 2>&1 && ! jar tf "$AREX_AGENT_JAR_PATH" >/dev/null 2>&1; then
    echo "ERROR: AREX agent jar is invalid or unreadable: $AREX_AGENT_JAR_PATH" >&2
    echo "Restore the jar or point AREX_AGENT_JAR_PATH to a valid copy before starting didi-system-b." >&2
    exit 1
  fi
}

if [ ! -f "$JAR_PATH" ] || [ "${DIDI_BUILD_ALWAYS:-0}" = "1" ]; then
  mvn -q -DskipTests package
fi

validate_arex_agent

exec java \
  -javaagent:"$AREX_AGENT_JAR_PATH" \
  -Darex.service.name=didi-car-uat \
  -Darex.storage.service.host="$AREX_STORAGE_URL" \
  -Darex.record.rate=100 \
  ${JAVA_OPTS:--Xms256m -Xmx512m} \
  -jar "$JAR_PATH"
