#!/bin/bash

# Script to run the Ollama Chat App with Vision Support
echo "🤖 Starting Ollama Chat App with Vision Support..."
echo ""
echo "📋 Prerequisites:"
echo "1. Make sure Ollama is running: ollama serve"
echo "2. Install at least one model:"
echo "   - Text model: ollama pull llama3.2:1b"
echo "   - Vision model: ollama pull qwen2.5-vl:7b"
echo "   - Vision model: ollama pull llava"
echo ""

# Check if streamlit is installed
if ! command -v streamlit &> /dev/null; then
    echo "📦 Installing Streamlit and dependencies..."
    uv sync
fi

echo "🚀 Launching Streamlit app..."
echo "✨ Features:"
echo "   - Chat with Ollama models"
echo "   - Upload and analyze images (with vision models)"
echo "   - Persistent chat history"  
echo "   - Session management"
echo "   - GPU support (if available)"
echo ""

# Run the streamlit app
streamlit run chat_app.py
