#!/bin/bash
# SecureScout Deployment Script

set -e  # Exit on any error

# Display banner
echo "==============================================="
echo "  SecureScout Deployment Script"
echo "==============================================="

# Check if .env file exists
if [ ! -f .env ]; then
  echo "Error: .env file not found."
  echo "Please create .env file from .env.template."
  exit 1
fi

# Function to check dependency
check_dependency() {
  if ! command -v $1 &> /dev/null; then
    echo "Error: $1 not found. Please install $1."
    exit 1
  else
    echo "✓ $1 installed"
  fi
}

# Check dependencies
echo "Checking dependencies..."
check_dependency docker
check_dependency docker-compose

# Create required directories if they don't exist
echo "Creating required directories..."
mkdir -p data logs reports

# Set proper permissions
chmod 755 data logs reports

# Build and start containers
echo "Building and starting containers..."
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# Wait for the backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..30}; do
  if curl -s http://localhost:8001/api/health | grep -q "ok"; then
    echo "✓ Backend is ready"
    break
  fi
  
  if [ $i -eq 30 ]; then
    echo "Error: Backend did not become ready in time."
    exit 1
  fi
  
  echo "Waiting... ($i/30)"
  sleep 2
done

# Display success message
echo "==============================================="
echo "  SecureScout has been deployed successfully!"
echo "==============================================="
echo "Access the application at: http://localhost"
echo "API is available at: http://localhost:8001"
echo ""
echo "To view logs, run: docker-compose logs -f"
echo "To stop the application, run: docker-compose down"
echo "==============================================="