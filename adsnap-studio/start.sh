#!/bin/bash

# AdSnap Studio Pro - Startup Script
echo "🎨 Starting AdSnap Studio Pro..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Check if requirements are installed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "Installing dependencies..."
    pip install -r requirements_improved.txt
    touch venv/.dependencies_installed
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your BRIA_API_KEY:"
    echo "echo 'BRIA_API_KEY=your_api_key_here' > .env"
    echo ""
fi

# Create logs directory
mkdir -p logs

# Start the application
echo "🚀 Launching AdSnap Studio Pro..."
echo "📊 Dashboard will be available at: http://localhost:8501"
echo "📝 Logs will be saved to: ./logs/"
echo ""

streamlit run app_improved.py