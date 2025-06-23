#!/bin/bash

# 🔍 Ollama Chat Interface - Validation Script
# This script validates that the setup was successful

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[CHECK]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[✅ PASS]${NC} $1"
}

print_error() {
    echo -e "${RED}[❌ FAIL]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[⚠️ WARN]${NC} $1"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

echo "=========================================="
echo -e "${BLUE}🔍 Validating Ollama Chat Interface Setup${NC}"
echo "=========================================="
echo

# Check project structure
print_status "Checking project structure..."
required_files=("main.py" "pyproject.toml" "uv.lock" "run_app.sh" "setup.sh")
missing_files=()

for file in "${required_files[@]}"; do
    if [[ -f "$file" ]]; then
        print_success "Found $file"
    else
        print_error "Missing $file"
        missing_files+=("$file")
    fi
done

required_dirs=("src" "assets" "docs" "tests")
missing_dirs=()

for dir in "${required_dirs[@]}"; do
    if [[ -d "$dir" ]]; then
        print_success "Found directory $dir/"
    else
        print_error "Missing directory $dir/"
        missing_dirs+=("$dir")
    fi
done

# Check Python (via UV)
print_status "Checking Python installation (via UV)..."
if command_exists uv; then
    if uv run python --version >/dev/null 2>&1; then
        PYTHON_VERSION=$(uv run python -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        print_success "Python $PYTHON_VERSION (managed by UV)"
        if [[ $(echo "$PYTHON_VERSION >= 3.12" | bc -l 2>/dev/null || echo "0") -eq 1 ]]; then
            print_success "✅ Python 3.12+ requirement met"
        else
            print_warning "⚠️ Python 3.12+ recommended, but UV can upgrade"
        fi
    else
        print_warning "Python not available via UV (run: uv sync)"
    fi
else
    print_error "UV not found - Python cannot be checked"
fi

# Also check system Python (optional)
print_status "Checking system Python (optional)..."
if command_exists python3; then
    SYSTEM_PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    print_success "System Python $SYSTEM_PYTHON_VERSION (not required - UV manages Python)"
else
    print_success "No system Python found (OK - UV will manage Python)"
fi

# Check UV
print_status "Checking UV package manager..."
if command_exists uv; then
    UV_VERSION=$(uv --version 2>/dev/null | cut -d' ' -f2 || echo "unknown")
    print_success "UV $UV_VERSION installed"
else
    print_error "UV package manager not found"
fi

# Check Ollama
print_status "Checking Ollama installation..."
if command_exists ollama; then
    print_success "Ollama installed"
    
    # Check if Ollama is running
    if ollama list >/dev/null 2>&1; then
        print_success "Ollama service is running"
        
        # Check for models
        MODEL_COUNT=$(ollama list | tail -n +2 | wc -l 2>/dev/null || echo "0")
        if [[ $MODEL_COUNT -gt 0 ]]; then
            print_success "$MODEL_COUNT Ollama model(s) installed"
            echo "   Available models:"
            ollama list | tail -n +2 | while read line; do
                model_name=$(echo "$line" | awk '{print $1}')
                echo "   - $model_name"
            done
        else
            print_warning "No Ollama models installed"
            echo "   Run: ollama pull llama3.2:1b"
        fi
    else
        print_warning "Ollama service not responding"
        echo "   Try: ollama serve (or restart the service)"
    fi
else
    print_error "Ollama not found"
fi

# Check Python environment
print_status "Checking Python environment..."
if [[ -d ".venv" ]]; then
    print_success "Virtual environment found"
else
    print_warning "Virtual environment not found (UV will create it)"
fi

# Check Python dependencies
print_status "Checking Python dependencies..."
if uv run python -c "import streamlit" 2>/dev/null; then
    print_success "Streamlit available"
else
    print_error "Streamlit not available"
fi

if uv run python -c "import ollama" 2>/dev/null; then
    print_success "Ollama Python client available"
else
    print_error "Ollama Python client not available"
fi

if uv run python -c "import PIL" 2>/dev/null; then
    print_success "Pillow (PIL) available"
else
    print_error "Pillow (PIL) not available"
fi

# Check if main application can be imported
print_status "Checking main application..."
if uv run python -c "import sys; sys.path.append('.'); import main" 2>/dev/null; then
    print_success "Main application can be imported"
else
    print_warning "Main application import issues (may still work)"
fi

# Check file permissions
print_status "Checking script permissions..."
scripts=("run_app.sh" "setup.sh" "validate.sh")
for script in "${scripts[@]}"; do
    if [[ -f "$script" ]]; then
        if [[ -x "$script" ]]; then
            print_success "$script is executable"
        else
            print_warning "$script is not executable (run: chmod +x $script)"
        fi
    fi
done

# Summary
echo
echo "=========================================="
echo -e "${BLUE}📋 Validation Summary${NC}"
echo "=========================================="

if [[ ${#missing_files[@]} -eq 0 && ${#missing_dirs[@]} -eq 0 ]]; then
    echo -e "${GREEN}✅ Project structure: COMPLETE${NC}"
else
    echo -e "${RED}❌ Project structure: INCOMPLETE${NC}"
    if [[ ${#missing_files[@]} -gt 0 ]]; then
        echo "   Missing files: ${missing_files[*]}"
    fi
    if [[ ${#missing_dirs[@]} -gt 0 ]]; then
        echo "   Missing directories: ${missing_dirs[*]}"
    fi
fi

if command_exists uv && command_exists ollama; then
    echo -e "${GREEN}✅ Core dependencies: INSTALLED${NC}"
else
    echo -e "${RED}❌ Core dependencies: MISSING${NC}"
    echo "   Run ./setup.sh to install missing components"
fi

echo
echo -e "${BLUE}🚀 Ready to start the application?${NC}"
echo "   ./run_app.sh"
echo "   OR"
echo "   uv run streamlit run main.py"
echo
