#!/bin/bash
set -e
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR_PATH="${SCRIPT_DIR}/target/loan-new-1.0.0-SNAPSHOT.jar"
if [ ! -f "$JAR_PATH" ]; then echo "Building..."; cd "${SCRIPT_DIR}/.." && mvn package -DskipTests -q; fi
echo "Starting loan-new on port 28082..."
nohup java -Dapp.name=loan-system -jar "$JAR_PATH" --server.port=28082 > "${SCRIPT_DIR}/loan-new.log" 2>&1 &
echo "PID: $!"
