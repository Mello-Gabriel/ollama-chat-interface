#!/bin/bash

# 🚀 Ollama Chat Interface - Streamlined Setup Script
# This script installs only what's necessary to get the project running

set -e  # Exit on any error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Helper functions
print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check if command exists
command_exists() { command -v "$1" >/dev/null 2>&1; }

# Clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    if ! command_exists git; then
        print_error "Git required. Install with: sudo apt install git (Linux) or brew install git (macOS)"
        exit 1
    fi
    
    REPO_URL="https://github.com/Mello-Gabriel/ollama-chat-interface.git"
    PROJECT_DIR="ollama-chat-interface"
    
    if [[ -d "$PROJECT_DIR" ]]; then
        print_warning "Directory exists. Removing and cloning fresh..."
        rm -rf "$PROJECT_DIR"
    fi
    
    git clone "$REPO_URL" && cd "$PROJECT_DIR" || exit 1
    print_success "Repository cloned to $(pwd)"
}

# Install UV (handles Python automatically)
install_uv() {
    print_status "Installing UV package manager..."
    
    if command_exists uv; then
        print_success "UV already installed"
        return
    fi
    
    if command_exists curl; then
        curl -LsSf https://astral.sh/uv/install.sh | sh
    else
        print_error "curl required for UV installation"
        exit 1
    fi
    
    export PATH="$HOME/.cargo/bin:$PATH"
    
    if ! command_exists uv; then
        print_error "UV installation failed"
        exit 1
    fi
    
    print_success "UV installed successfully"
}

# Install Ollama
install_ollama() {
    print_status "Installing Ollama..."
    
    if command_exists ollama; then
        print_success "Ollama already installed"
        return
    fi
    
    curl -fsSL https://ollama.com/install.sh | sh || {
        print_error "Ollama installation failed"
        exit 1
    }
    
    print_success "Ollama installed"
}

# Start Ollama service
start_ollama() {
    print_status "Starting Ollama..."
    
    # Start Ollama in background
    if ! pgrep -x "ollama" > /dev/null; then
        nohup ollama serve > /dev/null 2>&1 &
        sleep 3
        print_success "Ollama started"
    else
        print_success "Ollama already running"
    fi
}

# Setup Python environment and install dependencies
setup_environment() {
    print_status "Setting up Python environment..."
    
    # Create Python version file
    echo "3.12" > .python-version
    
    # Install dependencies (UV will install Python 3.12 automatically)
    uv sync || {
        print_error "Failed to install dependencies"
        exit 1
    }
    
    print_success "Environment setup complete"
}

# Install required model
install_model() {
    print_status "Installing vision model (qwen2.5vl:7b)..."
    print_warning "Model is ~4.7GB, this may take several minutes..."
    
    # Check if model already exists
    if ollama list | grep -q "qwen2.5vl:7b"; then
        print_success "Model already installed"
        return
    fi
    
    ollama pull qwen2.5vl:7b || {
        print_warning "Model installation failed. Install later with: ollama pull qwen2.5vl:7b"
        return
    }
    
    print_success "Vision model installed successfully"
}

# Make scripts executable
make_executable() {
    chmod +x run_app.sh setup.sh validate.sh 2>/dev/null || true
    print_success "Scripts made executable"
}

# Validate installation
validate_setup() {
    print_status "Validating setup..."
    
    # Test Python environment
    if uv run python -c "import streamlit, ollama, PIL" 2>/dev/null; then
        print_success "Python environment OK"
    else
        print_error "Python environment validation failed"
        exit 1
    fi
    
    # Test Ollama
    if ollama list >/dev/null 2>&1; then
        print_success "Ollama connection OK"
    else
        print_warning "Ollama not responding - you may need to restart it"
    fi
}

# Show final instructions
show_instructions() {
    echo
    echo "=========================================="
    echo -e "${GREEN}🎉 Setup Complete!${NC}"
    echo "=========================================="
    echo
    echo -e "${BLUE}📁 Location:${NC} $(pwd)"
    echo -e "${BLUE}🚀 Start app:${NC} ./run_app.sh"
    echo -e "${BLUE}🌐 URL:${NC} http://localhost:8501"
    echo -e "${BLUE}🔍 Validate:${NC} ./validate.sh"
    echo
    echo -e "${GREEN}Ready to chat with images! 🤖✨${NC}"
}

# Main execution
main() {
    echo "=========================================="
    echo -e "${BLUE}🚀 Ollama Chat Interface Setup${NC}"
    echo "=========================================="
    
    clone_repository
    install_uv
    install_ollama
    start_ollama
    setup_environment
    make_executable
    install_model
    validate_setup
    show_instructions
}

main "$@"
