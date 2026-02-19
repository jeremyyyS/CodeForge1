#!/bin/bash
# One-command startup for CodeForge
# Usage: bash run.sh

echo "Starting CodeForge..."

# Start backend in background
cd backend_new
python3 jeremy_final.py &
BACKEND_PID=$!
cd ..

# Wait for backend to be ready
sleep 2
echo "Backend running on http://localhost:8000 (PID: $BACKEND_PID)"

# Start frontend
cd codeforge-frontend
echo "Frontend starting on http://localhost:8501"
echo "Login: admin / admin123"
streamlit run Login.py --server.port 8501 --server.headless true
