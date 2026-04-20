#!/usr/bin/env bash
set -e

SCRIPT_DIR=$(cd "$(dirname "$0")" && pwd)
cd "$SCRIPT_DIR"

JAR_PATH="target/didi-system-a-1.0.0.jar"
AREX_STORAGE_URL="${AREX_STORAGE_URL:-127.0.0.1:8000}"

if [ ! -f "$JAR_PATH" ] || [ "${DIDI_BUILD_ALWAYS:-0}" = "1" ]; then
  mvn -q -DskipTests package
fi

exec java \
  -javaagent:/home/test/arex-agent/arex-agent.jar \
  -Darex.service.name=didi-car-sat \
  -Darex.storage.service.host="$AREX_STORAGE_URL" \
  -Darex.record.rate=100 \
  ${JAVA_OPTS:--Xms256m -Xmx512m} \
  -jar "$JAR_PATH"
