#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR_PATH="${SCRIPT_DIR}/target/credit-core-1.0.0-SNAPSHOT.jar"
APP_PORT="${CREDIT_PORT:-29081}"
APP_NAME="${CREDIT_APP_NAME:-credit-system}"
JAVA_AGENT_ARGS=""
AGENT_JAR="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-}}"
if [ -n "$AGENT_JAR" ] && [ -r "$AGENT_JAR" ]; then
  JAVA_AGENT_ARGS="-javaagent:${AGENT_JAR}"
fi
if [ ! -f "$JAR_PATH" ]; then
  echo "Building..."
  cd "${SCRIPT_DIR}/.." && mvn package -DskipTests -q
fi
echo "Starting credit-core on port ${APP_PORT}..."
nohup java ${JAVA_AGENT_ARGS} -Dapp.name="${APP_NAME}" -jar "$JAR_PATH" --server.port="${APP_PORT}" > "${SCRIPT_DIR}/credit-core.log" 2>&1 &
echo "PID: $!"
