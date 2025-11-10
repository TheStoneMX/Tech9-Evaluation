#!/bin/bash

# Setup script for Autonomous Research Assistant
# Tech9 Agentic AI Engineer Assessment

echo "=================================================="
echo "Autonomous Research Assistant - Setup"
echo "=================================================="

# Check Python version
echo ""
echo "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create virtual environment
echo ""
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✅ .env file created. Please add your API keys!"
    echo ""
    echo "Required API keys:"
    echo "  1. OPENAI_API_KEY - Get from https://platform.openai.com/api-keys"
    echo "  2. TAVILY_API_KEY - Get from https://tavily.com (free tier available)"
    echo ""
    echo "Edit .env and add your API keys before running the system."
else
    echo ""
    echo "✅ .env file already exists"
fi

echo ""
echo "=================================================="
echo "Setup Complete!"
echo "=================================================="
echo ""
echo "Next steps:"
echo "  1. Add your API keys to .env file"
echo "  2. Run: python main.py"
echo ""
echo "To activate the virtual environment in the future:"
echo "  source venv/bin/activate"
echo ""
