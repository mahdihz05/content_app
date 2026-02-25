#!/bin/sh
# backend/app/wait-for-it.sh
# usage: ./wait-for-it.sh host:port -- command args...
set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 host:port -- command"
  exit 1
fi

HOSTPORT="$1"
shift

# parse host:port
HOST="${HOSTPORT%:*}"
PORT="${HOSTPORT#*:}"

echo "Waiting for $HOST:$PORT ..."

while true; do
  python - <<PY >/dev/null 2>&1
import socket, sys
s = socket.socket()
try:
    s.settimeout(1.0)
    s.connect(("$HOST", int($PORT)))
    s.close()
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
  if [ $? -eq 0 ]; then
    echo "$HOST:$PORT is available"
    break
  fi
  echo "Waiting 2s for $HOST:$PORT ..."
  sleep 2
done

# shift past optional '--' if present
if [ "$1" = "--" ]; then
  shift
fi

exec "$@"