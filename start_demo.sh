#!/bin/bash

# Create necessary directories
mkdir -p logs reports data

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install flask flask-cors python-dotenv requests

# Kill any existing server processes
pkill -f "python demo_backend.py" || true

# Start the demo backend server
python demo_backend.py