#!/bin/bash

# DevSecOps Knowledge Chat - Local Development Setup
set -e

echo "Starting DevSecOps Knowledge Chat..."

# 1. Check Dependencies
echo "[1/3] Checking dependencies..."
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "Error: Ollama is not running. Please start it first."
    exit 1
fi

if ! ollama list | grep -q "qwen2.5:14b"; then
    echo "Pulling qwen2.5:14b model..."
    ollama pull qwen2.5:14b
fi

# 2. Setup Backend
echo "[2/3] Setting up backend..."
cd backend

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt
mkdir -p data/chroma_db

# Initialize data
python scripts/init_db.py
python scripts/ingest_policies.py

# 3. Start Services
echo "[3/3] Starting services..."

# Start backend
uvicorn app.main:app --reload --port 8000 > ../backend.log 2>&1 &
BACKEND_PID=$!

# Setup and start frontend
cd ../frontend
if [ ! -d "node_modules" ]; then
    npm install --silent
fi

npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!

echo "------------------------------------------------"
echo "Backend running at http://localhost:8000"
echo "Frontend running at http://localhost:3000"
echo "Logs written to backend.log and frontend.log"
echo "Press Ctrl+C to stop"
echo "------------------------------------------------"

# Cleanup trap
cleanup() {
    echo "Stopping services..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    exit 0
}
trap cleanup SIGINT SIGTERM

wait $BACKEND_PID $FRONTEND_PID
