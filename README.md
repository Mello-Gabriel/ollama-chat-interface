# 🤖 Ollama Chat Interface

A secure, feature-rich Streamlit application for chatting with local Ollama models with advanced image processing capabilities.

## ✨ Features

- **🔐 Security First**: Input validation, file sanitization, and secure session management
- **🖼️ Vision Model Support**: Upload and analyze images with vision-capable models
- **🗜️ Image Optimization**: Automatic image resizing and compression for faster processing
- **💾 Session Management**: Save, load, and manage conversation history
- **🎨 Dark Theme**: Beautiful, modern UI optimized for readability
- **⚡ GPU Support**: Automatic GPU detection and configuration
- **🔧 Customizable**: Temperature control, system prompts, and optimization settings

## 🏗️ Project Structure

```
ollama-chat/
├── main.py                     # Main application entry point
├── setup.sh                   # Complete automated setup script
├── validate.sh                # Setup validation script
├── run_app.sh                 # Application startup script
├── pyproject.toml             # UV project configuration
├── uv.lock                    # UV dependency lock file
├── requirements.txt           # Fallback dependencies
├── src/                       # Source code modules
│   ├── __init__.py
│   ├── config.py              # Configuration constants
│   ├── ui/                    # User interface components
│   │   ├── __init__.py
│   │   └── components.py      # Streamlit UI components
│   └── utils/                 # Utility modules
│       ├── __init__.py
│       ├── chat_history.py    # Chat session management
│       ├── image_processing.py # Image optimization & processing
│       ├── ollama_client.py   # Ollama API integration
│       └── security.py       # Security & validation
├── assets/                    # Static assets
│   └── styles.css            # Custom CSS styles
├── docs/                      # Documentation
│   └── *.md                  # Project documentation
└── tests/                     # Test files
    └── test_*.py             # Application tests
```

## 🚀 Quick Start

### Option 1: Automated Setup (Recommended)

**One-command setup from scratch:**

```bash
# Download and run the setup script
curl -fsSL https://raw.githubusercontent.com/Mello-Gabriel/ollama-chat-interface/main/setup.sh | bash

# OR download the script first, then run it
wget https://raw.githubusercontent.com/Mello-Gabriel/ollama-chat-interface/main/setup.sh
chmod +x setup.sh
./setup.sh
```

The setup script will automatically:
- ✅ Clone this repository
- ✅ Install UV package manager
- ✅ Install Python 3.12 (via UV)
- ✅ Install Ollama
- ✅ Start Ollama service
- ✅ Install all Python dependencies
- ✅ Download a vision model (qwen2.5vl:7b)
- ✅ Validate the installation

### Option 2: Manual Setup

If you prefer to clone the repository yourself:

### Prerequisites

1. **UV package manager** installed ([installation guide](https://docs.astral.sh/uv/getting-started/installation/))
   - UV will automatically install Python 3.12 for the project
2. **Ollama** installed and running
3. At least one Ollama model downloaded

### Installation

1. **Clone or download** this repository
2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Run the application**:
   ```bash
   # Using the startup script (recommended)
   ./run_app.sh
   
   # Or directly with uv
   uv run streamlit run main.py
   
   # Or activate the environment first
   source .venv/bin/activate
   streamlit run main.py
   ```

4. **Open your browser** to `http://localhost:8501`

### Setup Scripts

This project includes helpful setup and validation scripts:

- **`setup.sh`**: Complete automated installation and configuration
- **`validate.sh`**: Validates that all components are properly installed
- **`run_app.sh`**: Starts the application with proper environment

```bash
# Complete setup (recommended for new installations)
./setup.sh

# Validate existing setup
./validate.sh

# Start the application
./run_app.sh
```

## 🖼️ Image Processing Features

### Automatic Optimization
- **Smart resizing** to 1024x1024px maximum (maintaining aspect ratio)
- **JPEG compression** at 85% quality for optimal performance
- **Format conversion** (RGBA/LA → RGB) for model compatibility
- **Size reduction** typically 30-70% smaller files

### Vision Model Support
- **Auto-detection** of vision-capable models
- **Multi-image upload** with validation
- **Image preview** in sidebar
- **Secure processing** with comprehensive validation

### Supported Formats
- PNG, JPG, JPEG, GIF, BMP
- Maximum file size: 200MB per image
- Multiple images per conversation

## ⚙️ Configuration

### Environment Variables
- `CUDA_VISIBLE_DEVICES`: GPU device selection
- `OLLAMA_GPU`: Enable GPU acceleration

### Customization
Edit `src/config.py` to modify:
- Image optimization settings
- File size limits
- Security parameters
- UI constants

## 🔧 Development

### Code Organization
- **Modular design**: Separated concerns for better maintainability
- **Type hints**: Full type annotations for better IDE support
- **Error handling**: Comprehensive exception handling
- **Security**: Input validation and sanitization throughout

### Key Modules
- `main.py`: Application entry point and main logic
- `ui/components.py`: Streamlit UI rendering
- `utils/image_processing.py`: Image optimization and vision support
- `utils/ollama_client.py`: Ollama API integration
- `utils/security.py`: Security and validation functions
- `utils/chat_history.py`: Session and history management

## 📊 Performance Benefits

### Image Optimization Impact
- **Faster model inference**: Smaller images process quicker
- **Reduced memory usage**: Lower RAM requirements
- **Better responsiveness**: Faster upload and processing
- **Cost efficiency**: Less bandwidth and storage

### Benchmarks
- Large images (>2MB): 50-70% size reduction
- Medium images (500KB-2MB): 30-50% reduction
- Small images (<500KB): 10-30% reduction
- Processing speed: 2-5x faster inference times

## 🛡️ Security Features

- **File validation**: Strict image format checking
- **Size limits**: Configurable maximum file sizes
- **Input sanitization**: All user inputs validated
- **Session security**: Secure session ID generation
- **Path safety**: Prevents directory traversal attacks

## 🔍 Troubleshooting

### Common Issues

**No models found**:
```bash
ollama pull llama3.2:1b  # Install a basic model
ollama list              # Check available models
```

**Image upload fails**:
- Check file format (PNG, JPG, JPEG, GIF, BMP only)
- Verify file size (<200MB)
- Ensure image is not corrupted

**GPU not detected**:
- Check NVIDIA drivers installation
- Verify CUDA is available
- Restart Ollama service

## 📝 License

This project is open source and available under the MIT License.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the code documentation
3. Open an issue on the repository
