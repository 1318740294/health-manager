#!/bin/bash
set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"

cleanup() {
    echo ""
    echo "Shutting down services..."
    kill $(jobs -p) 2>/dev/null
    wait
    echo "All services stopped."
    exit 0
}
trap cleanup SIGINT SIGTERM

cd "$BACKEND_DIR"
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
echo "Backend starting on http://localhost:8000"

cd "$FRONTEND_DIR"
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi
npm run dev &
echo "Frontend starting on http://localhost:5173"

echo ""
echo "All services are running. Press Ctrl+C to stop."
echo "  Backend:  http://localhost:8000"
echo "  Frontend: http://localhost:5173"
echo ""

wait
