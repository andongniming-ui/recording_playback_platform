#!/usr/bin/env bash
# 一键启动脚本：arex-recorder 平台 + didi 被测系统
# 用法：
#   ./start-all.sh           # 启动全部
#   ./start-all.sh platform  # 只启动录制平台（MySQL + 后端 + 前端）
#   ./start-all.sh didi      # 只启动 didi 被测系统（需要 MySQL 已运行）

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
mkdir -p "$LOG_DIR"

MODE="${1:-all}"

# ─── 工具函数 ────────────────────────────────────────────────

log() { echo "[$(date '+%H:%M:%S')] $*"; }

wait_port() {
  local port=$1 name=$2 timeout=${3:-60}
  log "等待 $name 就绪（端口 $port）..."
  for i in $(seq 1 $timeout); do
    if nc -z 127.0.0.1 "$port" 2>/dev/null; then
      log "$name 已就绪"
      return 0
    fi
    sleep 1
  done
  log "警告：$name 端口 $port 超时未响应，继续..."
}

# ─── MySQL ───────────────────────────────────────────────────

start_mysql() {
  log "启动 MySQL 容器..."
  if docker ps --format '{{.Names}}' | grep -q '^arex-recorder-mysql$'; then
    log "MySQL 已在运行，跳过"
  else
    docker start arex-recorder-mysql
    wait_port 3307 "MySQL"
  fi
}

# ─── 后端 ────────────────────────────────────────────────────

start_backend() {
  log "启动后端（FastAPI）..."
  if lsof -i:8000 -sTCP:LISTEN -t &>/dev/null 2>&1; then
    log "端口 8000 已被占用，后端可能已在运行，跳过"
    return
  fi
  cd "$ROOT_DIR/backend"
  nohup uvicorn main:app --host 0.0.0.0 --port 8000 \
    > "$LOG_DIR/backend.log" 2>&1 &
  echo $! > "$LOG_DIR/backend.pid"
  log "后端已启动（PID $(cat "$LOG_DIR/backend.pid")，日志：logs/backend.log）"
  wait_port 8000 "后端"
}

# ─── 前端 ────────────────────────────────────────────────────

start_frontend() {
  log "启动前端（Vite）..."
  if lsof -i:3000 -sTCP:LISTEN -t &>/dev/null 2>&1; then
    log "端口 3000 已被占用，前端可能已在运行，跳过"
    return
  fi
  cd "$ROOT_DIR/frontend"
  nohup npm run dev \
    > "$LOG_DIR/frontend.log" 2>&1 &
  echo $! > "$LOG_DIR/frontend.pid"
  log "前端已启动（PID $(cat "$LOG_DIR/frontend.pid")，日志：logs/frontend.log）"
  wait_port 3000 "前端"
}

# ─── didi 系统 ───────────────────────────────────────────────

start_didi() {
  local name=$1 dir=$2 port=$3

  log "启动 $name..."
  if lsof -i:$port -sTCP:LISTEN -t &>/dev/null 2>&1; then
    log "端口 $port 已被占用，$name 可能已在运行，跳过"
    return
  fi

  cd "$dir"
  chmod +x start.sh
  DIDI_DB_PORT=3307 DIDI_SQL_INIT_MODE=never \
    nohup ./start.sh \
    > "$LOG_DIR/${name}.log" 2>&1 &
  echo $! > "$LOG_DIR/${name}.pid"
  log "$name 已启动（PID $(cat "$LOG_DIR/${name}.pid")，日志：logs/${name}.log）"
}

# ─── 主流程 ──────────────────────────────────────────────────

case "$MODE" in
  platform)
    start_mysql
    start_backend
    start_frontend
    ;;
  didi)
    start_didi "didi-system-a" "$ROOT_DIR/didi/didi-system-a" 18081
    start_didi "didi-system-b" "$ROOT_DIR/didi/didi-system-b" 18082
    ;;
  all|*)
    start_mysql
    start_backend
    start_frontend
    start_didi "didi-system-a" "$ROOT_DIR/didi/didi-system-a" 18081
    start_didi "didi-system-b" "$ROOT_DIR/didi/didi-system-b" 18082
    ;;
esac

echo ""
log "启动完成！"
echo "  前端：    http://localhost:3000"
echo "  后端 API：http://localhost:8000/docs"
echo "  System A：http://localhost:18081"
echo "  System B：http://localhost:18082"
echo ""
echo "  查看日志：tail -f logs/<服务名>.log"
echo "  停止服务：./stop-all.sh"
