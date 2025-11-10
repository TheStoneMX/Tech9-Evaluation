#!/bin/bash
# Quick script to add GROQ API key to .env file

echo "Enter your GROQ API key:"
read -r GROQ_KEY

# Update .env file with GROQ key
sed -i.bak "s/GROQ_API_KEY=your_groq_api_key_here/GROQ_API_KEY=$GROQ_KEY/" .env

echo "✅ GROQ API key added to .env file!"
echo "You can now run: ./run_streamlit_conda.sh"
