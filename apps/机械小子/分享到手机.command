#!/bin/zsh
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

if command -v python3 >/dev/null 2>&1; then
  cd "$ROOT_DIR"
  exec python3 tools/serve.py --host 0.0.0.0 --open
fi

echo "未找到 python3，无法启动局域网分享。"
exit 1
