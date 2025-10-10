#!/usr/bin/env bash
# 翻译API项目后台启动脚本 (Linux/macOS)
# 用法: ./start_background.sh [start|stop|status|restart]

set -euo pipefail

ACTION=${1:-help}
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PID_FILE="$SCRIPT_DIR/app.pid"
LOG_FILE="$SCRIPT_DIR/app.log"

command_exists() {
  command -v "$1" >/dev/null 2>&1
}

ensure_python() {
  if command_exists python; then PY=python
  elif command_exists python3; then PY=python3
  else
    echo "[错误] 未找到 Python，请安装后重试" >&2
    exit 1
  fi
}

ensure_env() {
  if [[ -f "$SCRIPT_DIR/.env" ]]; then return 0; fi
  if [[ -f "$SCRIPT_DIR/.env.example" ]]; then
    echo "[信息] 复制环境配置模板到 .env"
    cp "$SCRIPT_DIR/.env.example" "$SCRIPT_DIR/.env"
    echo "[提示] 请编辑 .env 配置 API 密钥后重新启动"
    exit 1
  else
    echo "[错误] 缺少 .env 与 .env.example" >&2
    exit 1
  fi
}

running_pid() {
  if [[ ! -f "$PID_FILE" ]]; then return 1; fi
  PID=$(tr -d '\n' < "$PID_FILE")
  if ps -p "$PID" > /dev/null 2>&1; then
    return 0
  else
    rm -f "$PID_FILE"
    return 1
  fi
}

start_app() {
  ensure_python
  ensure_env

  if running_pid; then
    PID=$(cat "$PID_FILE")
    echo "[警告] 应用已在运行 (PID: $PID)"
    echo "请先执行: ./start_background.sh stop"
    exit 1
  fi

  echo "[信息] 安装/更新依赖..."
  "$PY" -m pip install -r "$SCRIPT_DIR/requirements.txt" >/dev/null 2>&1 || true

  echo "[信息] 启动 FastAPI 应用 (后台模式)..."
  nohup "$PY" -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --reload \
    >> "$LOG_FILE" 2>&1 &
  echo $! > "$PID_FILE"
  sleep 1
  echo "[成功] 应用已启动，PID: $(cat "$PID_FILE")"
  echo "[信息] API 文档: http://127.0.0.1:8000/docs"
}

stop_app() {
  if running_pid; then
    PID=$(cat "$PID_FILE")
    echo "[信息] 停止应用 (PID: $PID)..."
    kill "$PID" 2>/dev/null || true
    sleep 1
    if ps -p "$PID" >/dev/null 2>&1; then
      echo "[信息] 发送 SIGKILL..."
      kill -9 "$PID" 2>/dev/null || true
    fi
    rm -f "$PID_FILE"
    echo "[成功] 应用已停止"
  else
    echo "[信息] 应用未在运行"
  fi
}

status_app() {
  if running_pid; then
    echo "[状态] 运行中 (PID: $(cat "$PID_FILE"))"
    echo "[信息] API 文档: http://127.0.0.1:8000/docs"
  else
    echo "[状态] 未运行"
  fi
}

case "$ACTION" in
  start) start_app ;;
  stop) stop_app ;;
  status) status_app ;;
  restart) stop_app; sleep 1; start_app ;;
  *)
    cat <<EOF
使用方法:
  ./start_background.sh start    启动应用(后台)
  ./start_background.sh stop     停止应用
  ./start_background.sh status   查看状态
  ./start_background.sh restart  重启应用
EOF
    ;;
esac
