#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR_PATH="${SCRIPT_DIR}/target/loan-old-1.0.0-SNAPSHOT.jar"
if [ ! -f "$JAR_PATH" ]; then echo "Building..."; cd "${SCRIPT_DIR}/.." && mvn package -DskipTests -q; fi
echo "Starting loan-old on port 28081..."
nohup java -Dapp.name=loan-system -jar "$JAR_PATH" --server.port=28081 > "${SCRIPT_DIR}/loan-old.log" 2>&1 &
echo "PID: $!"
