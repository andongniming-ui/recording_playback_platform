#!/usr/bin/env bash
# 停止所有服务

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"

log() { echo "[$(date '+%H:%M:%S')] $*"; }

stop_pid() {
  local name=$1 pidfile="$LOG_DIR/${1}.pid"
  if [ -f "$pidfile" ]; then
    local pid
    pid=$(cat "$pidfile")
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
      log "$name 已停止（PID $pid）"
    else
      log "$name 进程不存在（PID $pid），跳过"
    fi
    rm -f "$pidfile"
  else
    log "$name 无 PID 文件，跳过"
  fi
}

stop_pid "backend"
stop_pid "frontend"
stop_pid "didi-system-a"
stop_pid "didi-system-b"

log "全部服务已停止"
