#!/bin/bash
# Rental Compare System Startup Script
# Port: 20082

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PARENT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
JAR_DIR="$SCRIPT_DIR/target"
JAR_FILE="$JAR_DIR/rental-compare-1.0.0.jar"
LOG_DIR="/home/recording_playback_platform/runtime/logs/rental-compare"
AREX_AGENT_JAR="${AREX_AGENT_JAR:-/home/test/arex-platform_v1/backend/arex-agent/arex-agent.jar}"
AREX_STORAGE_HOST="${AREX_STORAGE_HOST:-127.0.0.1:8000}"
AREX_RECORD_RATE="${AREX_RECORD_RATE:-100}"

mkdir -p "$LOG_DIR"

# Build if jar doesn't exist
if [ ! -f "$JAR_FILE" ]; then
    echo "[rental-compare] Building..."
    cd "$PARENT_DIR" && mvn clean package -DskipTests -q
fi

if [ ! -f "$JAR_FILE" ]; then
    echo "[rental-compare] Build failed! JAR not found: $JAR_FILE"
    exit 1
fi

if command -v lsof >/dev/null 2>&1; then
    OLD_PIDS="$(lsof -ti tcp:20082 || true)"
    if [ -n "$OLD_PIDS" ]; then
        echo "[rental-compare] Stopping existing process on port 20082: $OLD_PIDS"
        kill $OLD_PIDS 2>/dev/null || true
        sleep 2
    fi
fi

JAVA_AGENT_OPTS=()
if [ -f "$AREX_AGENT_JAR" ]; then
    JAVA_AGENT_OPTS=(
        "-javaagent:$AREX_AGENT_JAR"
        "-Darex.service.name=rental-system-compare"
        "-Darex.storage.service.host=$AREX_STORAGE_HOST"
        "-Darex.record.rate=$AREX_RECORD_RATE"
    )
else
    echo "[rental-compare] WARN: AREX agent jar not found: $AREX_AGENT_JAR; starting without agent"
fi

echo "[rental-compare] Starting on port 20082..."
nohup java "${JAVA_AGENT_OPTS[@]}" -jar "$JAR_FILE" \
    --server.port=20082 \
    --spring.datasource.url="jdbc:mysql://localhost:3307/rental_db?useSSL=false&allowPublicKeyRetrieval=true&serverTimezone=Asia/Shanghai&characterEncoding=utf8" \
    --spring.datasource.username=root \
    --spring.datasource.password=root123 \
    > "$LOG_DIR/rental-compare.log" 2>&1 < /dev/null &
echo "[rental-compare] PID: $!"
echo "[rental-compare] Logs: $LOG_DIR/rental-compare.log"
