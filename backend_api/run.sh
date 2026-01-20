#!/bin/bash

# Script to run Backend API

echo "🚀 Starting Fitness AI Coach Backend API..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "⚠️  Virtual environment not found. Creating..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "📦 Installing dependencies..."
pip install -q -r backend_api/requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Please create it from .env.example"
    exit 1
fi

# Create uploads directory
mkdir -p uploads

# Run API
echo ""
echo "✅ Starting API on http://localhost:8000"
echo "📚 Swagger UI: http://localhost:8000/docs"
echo "📖 ReDoc: http://localhost:8000/redoc"
echo ""

python -m backend_api.main
