#!/bin/bash

# Run Streamlit with Conda Environment
# This script activates the langgraph conda environment and runs the Streamlit app

echo "=================================================="
echo "Autonomous Research Assistant - Streamlit UI"
echo "=================================================="
echo ""

# Get conda base path
CONDA_BASE=$(conda info --base)

# Source conda
source "$CONDA_BASE/etc/profile.d/conda.sh"

# Activate langgraph environment
echo "Activating conda environment: langgraph"
conda activate langgraph

# Check if activation was successful
if [ $? -ne 0 ]; then
    echo "Error: Failed to activate langgraph conda environment"
    echo "Please ensure the environment exists: conda env list"
    exit 1
fi

echo "✅ Conda environment activated: langgraph"
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found"
    echo "Please create it and add your API keys:"
    echo "  cp .env.example .env"
    echo ""
fi

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "Installing Streamlit in current environment..."
    pip install streamlit --quiet
fi

echo "🚀 Starting Streamlit app..."
echo ""
echo "The app will open in your browser at: http://localhost:8501"
echo ""
echo "To stop the app, press Ctrl+C"
echo ""

# Open browser and run Streamlit
open http://localhost:8501
streamlit run streamlit_app.py
