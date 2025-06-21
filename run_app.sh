#!/bin/bash
# Startup script for Ollama Chat Interface

echo "🚀 Starting Ollama Chat Interface..."
echo "📁 Working directory: $(pwd)"

# Check if main.py exists
if [ ! -f "main.py" ]; then
    echo "❌ Error: main.py not found in current directory"
    echo "💡 Please run this script from the project root directory"
    exit 1
fi

# Check if src directory exists
if [ ! -d "src" ]; then
    echo "❌ Error: src directory not found"
    echo "💡 Please ensure the project structure is correct"
    exit 1
fi

# Start the application
echo "🌟 Launching Streamlit application..."
streamlit run main.py --server.port 8501 --server.address 0.0.0.0
