#!/bin/bash

# Run Streamlit Web Interface for Autonomous Research Assistant

echo "=================================================="
echo "Starting Autonomous Research Assistant Web UI"
echo "=================================================="
echo ""

# Check if virtual environment is activated
if [[ -z "$VIRTUAL_ENV" ]]; then
    echo "Virtual environment not activated. Activating..."
    if [ -f "venv/bin/activate" ]; then
        source venv/bin/activate
    else
        echo "Error: Virtual environment not found. Please run setup.sh first."
        exit 1
    fi
fi

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Error: .env file not found. Please create it and add your API keys."
    echo "Copy .env.example to .env and add your keys:"
    echo "  cp .env.example .env"
    exit 1
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Streamlit not found. Installing dependencies..."
    pip install -r requirements.txt
fi

echo ""
echo "✅ Starting Streamlit app..."
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo ""
echo "To stop the app, press Ctrl+C"
echo ""

# Run Streamlit
streamlit run streamlit_app.py
