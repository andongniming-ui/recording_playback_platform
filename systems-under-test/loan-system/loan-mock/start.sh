#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
JAR_PATH="${SCRIPT_DIR}/target/loan-mock-1.0.0-SNAPSHOT.jar"
if [ ! -f "$JAR_PATH" ]; then echo "Building..."; cd "${SCRIPT_DIR}/.." && mvn package -DskipTests -q; fi
echo "Starting loan-mock on port 28083..."
nohup java -Dapp.name=loan-mock -jar "$JAR_PATH" --server.port=28083 > "${SCRIPT_DIR}/loan-mock.log" 2>&1 &
echo "PID: $!"
