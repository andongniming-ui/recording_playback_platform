#!/usr/bin/env bash
# 一键启动脚本：录制回放平台 + didi 被测系统
# 用法：
#   ./start-all.sh           # 启动全部
#   ./start-all.sh platform  # 只启动录制平台（MySQL + 后端 + 前端）
#   ./start-all.sh didi      # 只启动 didi 被测系统（需要 MySQL 已运行）

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLATFORM_DIR="$ROOT_DIR/platform"
SYSTEMS_DIR="$ROOT_DIR/systems-under-test"
LOG_DIR="$ROOT_DIR/runtime/logs"
mkdir -p "$LOG_DIR"

MODE="${1:-all}"
AREX_AGENT_JAR_PATH="${AREX_AGENT_JAR_PATH:-${AR_AREX_AGENT_JAR_PATH:-/home/test/arex-agent/arex-agent.jar}}"
FRONTEND_PORT=5173
MYSQL_CONTAINER=arex-recorder-mysql
MYSQL_PORT=3307
MYSQL_VOLUME=arex-recorder_mysql_data
MYSQL_DATABASE=arex_recorder
MYSQL_USER=arex
MYSQL_PASSWORD=arex123

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
  return 1
}

http_ok() {
  local url=$1
  curl -fsS --max-time 3 "$url" >/dev/null 2>&1
}

mysql_port_ready() {
  nc -z 127.0.0.1 "$MYSQL_PORT" 2>/dev/null
}

mysql_data_volume() {
  docker inspect "$MYSQL_CONTAINER" \
    --format '{{range .Mounts}}{{if eq .Destination "/var/lib/mysql"}}{{.Name}}{{end}}{{end}}' \
    2>/dev/null || true
}

rename_conflicting_mysql_container() {
  if ! docker ps -a --format '{{.Names}}' | grep -qx "$MYSQL_CONTAINER"; then
    return 0
  fi

  local mounted_volume new_name
  mounted_volume="$(mysql_data_volume)"
  if [ "$mounted_volume" = "$MYSQL_VOLUME" ] && mysql_port_ready; then
    return 0
  fi

  new_name="${MYSQL_CONTAINER}-detached-$(date +%Y%m%d%H%M%S)"
  log "MySQL container name is occupied but not usable for this project; preserving it as $new_name"
  docker rename "$MYSQL_CONTAINER" "$new_name"
}

assert_mysql_volume() {
  local mounted_volume
  mounted_volume="$(mysql_data_volume)"
  if [ "$mounted_volume" != "$MYSQL_VOLUME" ]; then
    log "ERROR: MySQL is mounted on '$mounted_volume', expected '$MYSQL_VOLUME'. Refusing to continue to avoid using the wrong database."
    exit 1
  fi
}

log_mysql_data_summary() {
  local counts total
  counts="$(docker exec -e MYSQL_PWD="$MYSQL_PASSWORD" "$MYSQL_CONTAINER" \
    mysql -u"$MYSQL_USER" -N "$MYSQL_DATABASE" \
      -e "SELECT 'application', COUNT(*) FROM application UNION ALL SELECT 'recording_session', COUNT(*) FROM recording_session UNION ALL SELECT 'recording', COUNT(*) FROM recording UNION ALL SELECT 'arex_mocker', COUNT(*) FROM arex_mocker UNION ALL SELECT 'replay_job', COUNT(*) FROM replay_job UNION ALL SELECT 'test_case', COUNT(*) FROM test_case;" \
    2>/dev/null || true)"
  if [ -z "$counts" ]; then
    log "WARNING: Unable to read MySQL data summary; backend health check will still verify connectivity."
    return 0
  fi
  log "MySQL data summary: $(echo "$counts" | awk '{printf "%s=%s ", $1, $2}')"
  total="$(echo "$counts" | awk '{sum += $2} END {print sum + 0}')"
  if [ "$total" = "0" ]; then
    log "WARNING: Current MySQL business tables are empty. If you expected old test data, stop now and check the active Docker volume."
  fi
}

restart_process_on_port() {
  local port=$1 name=$2
  local pids
  pids=$(lsof -ti:"$port" 2>/dev/null || true)
  if [ -z "$pids" ]; then
    return 0
  fi
  log "$name 端口 $port 已被占用，但健康检查失败，准备重启（PID: $pids）"
  kill $pids 2>/dev/null || true
  sleep 1
  pids=$(lsof -ti:"$port" 2>/dev/null || true)
  if [ -n "$pids" ]; then
    log "$name 进程仍未退出，执行强制终止（PID: $pids）"
    kill -9 $pids 2>/dev/null || true
    sleep 1
  fi
}

validate_arex_agent() {
  if [ ! -f "$AREX_AGENT_JAR_PATH" ]; then
    log "错误：AREX agent jar 不存在：$AREX_AGENT_JAR_PATH"
    log "请设置 AREX_AGENT_JAR_PATH 或 AR_AREX_AGENT_JAR_PATH 指向有效的 arex-agent.jar"
    exit 1
  fi

  if [ ! -s "$AREX_AGENT_JAR_PATH" ]; then
    log "错误：AREX agent jar 为空文件：$AREX_AGENT_JAR_PATH"
    log "请先恢复有效的 arex-agent.jar，再启动 didi 系统"
    exit 1
  fi

  if command -v jar >/dev/null 2>&1 && ! jar tf "$AREX_AGENT_JAR_PATH" >/dev/null 2>&1; then
    log "错误：AREX agent jar 无法读取：$AREX_AGENT_JAR_PATH"
    log "请先恢复有效的 arex-agent.jar，再启动 didi 系统"
    exit 1
  fi
}

# ─── MySQL ───────────────────────────────────────────────────

start_mysql() {
  log "启动 MySQL 容器..."
  if docker ps --format '{{.Names}}' | grep -q '^arex-recorder-mysql$'; then
    log "MySQL 已在运行，跳过"
  else
    docker compose -f "$PLATFORM_DIR/docker-compose.yml" up -d db
    wait_port 3307 "MySQL" || true
  fi
}

# ─── 后端 ────────────────────────────────────────────────────

start_backend() {
  log "启动后端（FastAPI）..."
  if lsof -i:8000 -sTCP:LISTEN -t &>/dev/null 2>&1; then
    if http_ok "http://127.0.0.1:8000/api/health"; then
      log "后端健康检查通过，跳过启动"
      return
    fi
    restart_process_on_port 8000 "后端"
  fi
  cd "$PLATFORM_DIR/backend"
  nohup uvicorn main:app --host 0.0.0.0 --port 8000 \
    > "$LOG_DIR/backend.log" 2>&1 &
  echo $! > "$LOG_DIR/backend.pid"
  log "后端已启动（PID $(cat "$LOG_DIR/backend.pid")，日志：logs/backend.log）"
  wait_port 8000 "后端" || true
  if http_ok "http://127.0.0.1:8000/api/health"; then
    log "后端健康检查通过"
  else
    log "错误：后端端口已监听，但 /api/health 不可用，请检查 logs/backend.log"
    exit 1
  fi
}

# ─── 前端 ────────────────────────────────────────────────────

start_frontend() {
  log "启动前端（Vite）..."
  if lsof -i:$FRONTEND_PORT -sTCP:LISTEN -t &>/dev/null 2>&1; then
    log "端口 $FRONTEND_PORT 已被占用，前端可能已在运行，跳过"
    return
  fi
  cd "$PLATFORM_DIR/frontend"
  nohup npm run dev -- --host 0.0.0.0 \
    > "$LOG_DIR/frontend.log" 2>&1 &
  echo $! > "$LOG_DIR/frontend.pid"
  log "前端已启动（PID $(cat "$LOG_DIR/frontend.pid")，日志：logs/frontend.log）"
  wait_port "$FRONTEND_PORT" "前端" || true
}

# ─── didi 系统 ───────────────────────────────────────────────

start_didi() {
  local name=$1 dir=$2 port=$3

  validate_arex_agent
  log "启动 $name..."
  if lsof -i:$port -sTCP:LISTEN -t &>/dev/null 2>&1; then
    log "端口 $port 已被占用，$name 可能已在运行，跳过"
    return
  fi

  cd "$dir"
  chmod +x start.sh
  AREX_AGENT_JAR_PATH="$AREX_AGENT_JAR_PATH" DIDI_DB_PORT=3307 DIDI_SQL_INIT_MODE=never \
    nohup ./start.sh \
    > "$LOG_DIR/${name}.log" 2>&1 &
  echo $! > "$LOG_DIR/${name}.pid"
  log "$name 已启动（PID $(cat "$LOG_DIR/${name}.pid")，AREX Agent：$AREX_AGENT_JAR_PATH，日志：logs/${name}.log）"
  if ! wait_port "$port" "$name" 30; then
    log "错误：$name 启动后端口 $port 未就绪，请检查 logs/${name}.log"
    exit 1
  fi
}

# ─── 主流程 ──────────────────────────────────────────────────

start_mysql() {
  log "Starting MySQL container..."
  if docker ps --format '{{.Names}}' | grep -qx "$MYSQL_CONTAINER" && mysql_port_ready; then
    assert_mysql_volume
    log "MySQL is already running"
  else
    rename_conflicting_mysql_container
    docker volume inspect "$MYSQL_VOLUME" >/dev/null 2>&1 || docker volume create "$MYSQL_VOLUME" >/dev/null
    docker compose -f "$PLATFORM_DIR/docker-compose.yml" up -d db
    wait_port "$MYSQL_PORT" "MySQL" || true
    assert_mysql_volume
  fi
  log_mysql_data_summary
}

case "$MODE" in
  platform)
    start_mysql
    start_backend
    start_frontend
    ;;
  didi)
    start_didi "didi-system-a" "$SYSTEMS_DIR/didi/didi-system-a" 18081
    start_didi "didi-system-b" "$SYSTEMS_DIR/didi/didi-system-b" 18082
    ;;
  all|*)
    start_mysql
    start_backend
    start_frontend
    start_didi "didi-system-a" "$SYSTEMS_DIR/didi/didi-system-a" 18081
    start_didi "didi-system-b" "$SYSTEMS_DIR/didi/didi-system-b" 18082
    ;;
esac

echo ""
log "启动完成！"
echo "  前端：    http://localhost:$FRONTEND_PORT"
echo "  后端 API：http://localhost:8000/docs"
echo "  System A：http://localhost:18081"
echo "  System B：http://localhost:18082"
echo ""
echo "  查看日志：tail -f runtime/logs/<服务名>.log"
echo "  停止服务：./stop-all.sh"
