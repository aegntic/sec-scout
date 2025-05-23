#!/bin/bash

# Start SecureScout servers in background

echo "Starting SecureScout servers..."

# Kill any existing processes
pkill -f "python.*app.py" 2>/dev/null || true
pkill -f "node.*react-scripts" 2>/dev/null || true
sleep 2

# Set environment
export PYTHONPATH="/home/qubit/Downloads/secure-scout/SecureScout:$PYTHONPATH"

# Start backend
echo "Starting backend on port 8001..."
cd /home/qubit/Downloads/secure-scout/SecureScout/backend
nohup python app.py > backend.log 2>&1 &
BACKEND_PID=$!
echo "Backend PID: $BACKEND_PID"

# Wait for backend to start
sleep 3

# Start frontend
echo "Starting frontend on port 3005..."
cd /home/qubit/Downloads/secure-scout/SecureScout/frontend
export PORT=3005
nohup npm start > frontend.log 2>&1 &
FRONTEND_PID=$!
echo "Frontend PID: $FRONTEND_PID"

# Save PIDs
echo $BACKEND_PID > /tmp/securescout-backend.pid
echo $FRONTEND_PID > /tmp/securescout-frontend.pid

echo ""
echo "Servers starting..."
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3005"
echo ""
echo "To stop servers: pkill -f 'python.*app.py' && pkill -f 'node.*react-scripts'"
echo ""
echo "Waiting for servers to fully start..."
sleep 10

# Check if servers are running
if curl -s http://localhost:8001/api/health > /dev/null; then
    echo "✓ Backend is running"
else
    echo "✗ Backend failed to start - check backend/backend.log"
fi

if curl -s http://localhost:3005 > /dev/null 2>&1; then
    echo "✓ Frontend is running"
else
    echo "✗ Frontend may still be starting - check frontend/frontend.log"
fi

echo ""
echo "Logs:"
echo "- Backend: backend/backend.log"
echo "- Frontend: frontend/frontend.log"