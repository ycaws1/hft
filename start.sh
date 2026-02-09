#!/usr/bin/env bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"

cleanup() {
  echo ""
  echo "Shutting down..."
  kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
  wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
  echo "Done."
}
trap cleanup EXIT INT TERM

# Check PostgreSQL is running
if ! pg_isready -q 2>/dev/null; then
  echo "PostgreSQL is not running. Start it with: brew services start postgresql"
  exit 1
fi

# Start backend
echo "Starting backend on http://localhost:8000 ..."
cd "$ROOT_DIR/backend"
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
echo "Starting frontend on http://localhost:3000 ..."
cd "$ROOT_DIR/frontend"
npm run dev &
FRONTEND_PID=$!

echo ""
echo "Both services started. Press Ctrl+C to stop."
wait
