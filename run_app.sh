#!/bin/bash
# Startup script for Ollama Chat Interface

echo "🚀 Starting Ollama Chat Interface..."
echo "📁 Working directory: $(pwd)"

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv command not found"
    echo "💡 Please install uv: https://docs.astral.sh/uv/"
    exit 1
fi

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

# Check if .venv directory exists
if [ ! -d ".venv" ]; then
    echo "❌ Error: .venv directory not found"
    echo "💡 Please create the virtual environment first:"
    echo "   uv venv"
    echo "   uv pip install -r requirements.txt"
    exit 1
fi

# Check if Python is available in virtual environment
if [ ! -f ".venv/bin/python" ]; then
    echo "❌ Error: Python not found in virtual environment"
    echo "💡 Please ensure the virtual environment is properly set up"
    exit 1
fi

# Set Python executable path
PYTHON_EXEC=".venv/bin/python"

# Check if Streamlit is installed in the virtual environment
if ! $PYTHON_EXEC -c "import streamlit" &> /dev/null; then
    echo "❌ Error: Streamlit is not installed in virtual environment"
    echo "💡 Please install requirements: uv pip install -r requirements.txt"
    exit 1
fi

# Check if Ollama is available
if ! command -v ollama &> /dev/null; then
    echo "⚠️  Warning: Ollama command not found in PATH"
    echo "💡 Make sure Ollama is installed and running"
fi

# Start the application
echo "🌟 Launching Streamlit application..."
echo "🌐 Application will be available at: http://localhost:8501"
echo "🔧 Configuration: Port 8501, Address 0.0.0.0"
echo ""

# Run Streamlit with better error handling
if $PYTHON_EXEC -m streamlit run main.py --server.port 8501 --server.address 0.0.0.0 --server.headless true; then
    echo "✅ Application started successfully"
else
    echo "❌ Failed to start Streamlit application"
    echo "💡 Check the error messages above for troubleshooting"
    exit 1
fi
