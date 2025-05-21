#!/bin/bash
# SecureScout Test Runner

set -e

# Display banner
echo "====================================================="
echo "  SecureScout Test Runner"
echo "====================================================="

# Check for pytest
if ! command -v pytest &> /dev/null; then
    echo "Error: pytest not found. Please install it with 'pip install pytest pytest-asyncio pytest-cov'"
    exit 1
fi

# Check for Python virtual environment
if [ -z "$VIRTUAL_ENV" ]; then
    echo "Warning: No virtual environment detected."
    echo "It is recommended to run tests in a virtual environment."
    echo
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Create temporary directories for tests
echo "Creating temporary test directories..."
mkdir -p test_data test_logs test_reports

# Run backend unit tests
echo "====================================================="
echo "Running backend unit tests..."
echo "====================================================="
pytest tests/unit -v

# Run integration tests
echo "====================================================="
echo "Running integration tests..."
echo "====================================================="
pytest tests/integration -v

# Setup for frontend tests if needed
if [ -d "frontend" ]; then
    echo "====================================================="
    echo "Running frontend tests..."
    echo "====================================================="
    
    if [ -f "frontend/package.json" ]; then
        cd frontend
        npm test
        cd ..
    else
        echo "No frontend tests found."
    fi
fi

# Run coverage report
echo "====================================================="
echo "Generating coverage report..."
echo "====================================================="
pytest --cov=backend --cov-report=term-missing --cov-report=html:coverage_report tests/

# Clean up temporary directories
echo "Cleaning up..."
rm -rf test_data test_logs test_reports

echo "====================================================="
echo "  All tests completed!"
echo "====================================================="
echo "Coverage report available in coverage_report/index.html"