#!/usr/bin/env bash
set -e

DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"
PROJECT_ROOT="$(dirname "$DIR")"

echo "=========================================================="
echo "  Starting FashionPulse AI Platform (Local Dev Server)    "
echo "=========================================================="

cd "$PROJECT_ROOT"

# 1. Initialize DB if not present
if [ ! -f "fashionpulse.db" ]; then
    echo "[1/3] Seeding initial fashion observations..."
    python scripts/seed_demo_data.py
fi

# 2. Start FastAPI Backend in background
echo "[2/3] Starting FastAPI backend on http://127.0.0.1:8000..."
uvicorn app.main:app --app-dir backend --host 127.0.0.1 --port 8000 --reload &
BACKEND_PID=$!

# Trap exit to kill backend
trap "kill $BACKEND_PID" EXIT

# 3. Start Frontend Vite
echo "[3/3] Starting Vite frontend on http://localhost:5173..."
cd "$PROJECT_ROOT/frontend"
npm run dev
