#!/bin/bash

# CodeForge - One Click Run Script
# Starts both backend (FastAPI) and frontend (Streamlit) together

set -e

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend_new"
FRONTEND_DIR="$ROOT_DIR/codeforge-frontend"

echo "============================="
echo "  CodeForge - Starting Up"
echo "============================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "Python 3 is required but not found. Please install Python 3.8+."
    exit 1
fi
echo "Python 3 found: $(python3 --version)"

# Install dependencies
if [ -f "$FRONTEND_DIR/requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r "$FRONTEND_DIR/requirements.txt" --quiet 2>/dev/null
    echo "Dependencies ready."
fi
echo ""

# Cleanup function - kill both processes on exit
cleanup() {
    echo ""
    echo "Shutting down CodeForge..."
    if [ -n "$BACKEND_PID" ] && kill -0 "$BACKEND_PID" 2>/dev/null; then
        kill "$BACKEND_PID" 2>/dev/null
    fi
    if [ -n "$FRONTEND_PID" ] && kill -0 "$FRONTEND_PID" 2>/dev/null; then
        kill "$FRONTEND_PID" 2>/dev/null
    fi
    wait 2>/dev/null
    echo "CodeForge stopped."
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# Start Backend
echo "Starting Backend (FastAPI) on http://localhost:8000 ..."
cd "$BACKEND_DIR"
python3 jeremy_final.py &
BACKEND_PID=$!

# Give backend a moment to start
sleep 2

# Verify backend started
if ! kill -0 "$BACKEND_PID" 2>/dev/null; then
    echo "Backend failed to start. Check logs above."
    exit 1
fi
echo "Backend running (PID $BACKEND_PID)"
echo ""

# Start Frontend
echo "Starting Frontend (Streamlit) on http://localhost:8501 ..."
cd "$FRONTEND_DIR"
streamlit run Login.py --server.headless true &
FRONTEND_PID=$!

sleep 2

if ! kill -0 "$FRONTEND_PID" 2>/dev/null; then
    echo "Frontend failed to start. Check logs above."
    exit 1
fi
echo "Frontend running (PID $FRONTEND_PID)"
echo ""

echo "============================="
echo "  CodeForge is running!"
echo "  Frontend: http://localhost:8501"
echo "  Backend:  http://localhost:8000"
echo "  Press Ctrl+C to stop both."
echo "============================="

# Wait for either process to exit
wait -n "$BACKEND_PID" "$FRONTEND_PID" 2>/dev/null
