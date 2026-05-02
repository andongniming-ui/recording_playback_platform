#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR_PATH="${SCRIPT_DIR}/target/credit-mock-1.0.0-SNAPSHOT.jar"
APP_PORT="${CREDIT_MOCK_PORT:-29083}"
if [ ! -f "$JAR_PATH" ]; then
  echo "Building..."
  cd "${SCRIPT_DIR}/.." && mvn package -DskipTests -q
fi
echo "Starting credit-mock on port ${APP_PORT}..."
nohup java -Dapp.name=credit-mock -jar "$JAR_PATH" --server.port="${APP_PORT}" > "${SCRIPT_DIR}/credit-mock.log" 2>&1 &
echo "PID: $!"
