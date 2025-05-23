#!/bin/bash

echo "🚀 Starting SecureScout locally..."

# Set environment variables
export PYTHONPATH="${PWD}:${PYTHONPATH}"
export FLASK_ENV=development
export FLASK_DEBUG=1

# Kill any existing processes
echo "🔄 Cleaning up existing processes..."
pkill -f "python.*app.py" || true
pkill -f "node.*react-scripts" || true
sleep 2

# Start backend
echo "🔧 Starting backend server..."
cd backend
python app.py &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8001/api/health > /dev/null 2>&1; then
    echo "✅ Backend is running on http://localhost:8001"
else
    echo "❌ Backend failed to start. Check logs."
fi

# Start frontend
echo "🎨 Starting frontend..."
cd frontend
PORT=3002 npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "📋 SecureScout is starting up!"
echo "Backend: http://localhost:8001"
echo "Frontend: http://localhost:3002"
echo ""
echo "Default credentials:"
echo "Username: admin"
echo "Password: admin123"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for interrupt
trap "echo '🛑 Stopping services...'; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT
wait