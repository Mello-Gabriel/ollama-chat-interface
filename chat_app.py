"""Ollama Chat Interface - A secure Streamlit application for chatting with local Ollama models.

Security features:
- Input validation and sanitization
- File upload restrictions
- Session ID validation
- Safe directory operations
"""

import base64
import json
import os
import re
from datetime import UTC, datetime
from io import BytesIO
from pathlib import Path

import ollama
import streamlit as st
from PIL import Image

# Security constants
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB to match UI display
MAX_CONTENT_LENGTH = 100
ALLOWED_IMAGE_TYPES = {"png", "jpg", "jpeg", "gif", "bmp"}
SESSION_ID_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")
MAX_SESSION_ID_LENGTH = 50

# Image optimization constants
MAX_IMAGE_WIDTH = 1024  # Reduzir para 1024px de largura máxima
MAX_IMAGE_HEIGHT = 1024  # Reduzir para 1024px de altura máxima
IMAGE_QUALITY = 85  # Qualidade de compressão para JPEG (85% é um bom balance)
OPTIMIZE_IMAGES = True  # Flag para ativar/desativar otimização


def validate_session_id(session_id: str) -> bool:
    """Validate session ID for security."""
    if not session_id or len(session_id) > MAX_SESSION_ID_LENGTH:
        return False
    return bool(SESSION_ID_PATTERN.match(session_id))


def sanitize_file_upload(uploaded_file) -> bool:
    """Validate uploaded file for security with detailed error reporting."""
    if uploaded_file is None:
        st.error("❌ No file provided")
        return False

    # Check file size first (only if size attribute exists)
    if hasattr(uploaded_file, "size"):
        if uploaded_file.size == 0:
            st.error("❌ File is empty")
            return False
        if uploaded_file.size > MAX_FILE_SIZE:
            size_mb = uploaded_file.size / (1024 * 1024)
            max_size_mb = MAX_FILE_SIZE / (1024 * 1024)
            st.error(f"❌ File too large: {size_mb:.1f}MB. Maximum: {max_size_mb}MB")
            return False

    # Check file name exists
    if not hasattr(uploaded_file, "name") or not uploaded_file.name:
        st.error("❌ File has no name")
        return False

    # Check file type by extension
    file_extension = (
        uploaded_file.name.split(".")[-1].lower() if "." in uploaded_file.name else ""
    )

    if not file_extension:
        st.error("❌ File has no extension")
        return False

    if file_extension not in ALLOWED_IMAGE_TYPES:
        st.error(
            f"❌ Invalid file type '{file_extension}'. Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
        )
        return False

    # Try to verify it's actually an image by opening it
    try:
        # Save current position
        original_position = (
            uploaded_file.tell() if hasattr(uploaded_file, "tell") else 0
        )

        # Reset to beginning for validation
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(0)

        # Try to open as image
        with Image.open(uploaded_file) as img:
            # Basic image validation
            img.verify()  # This will raise an exception if the image is corrupt

            # Optional: Check image format matches extension
            img_format = img.format.lower() if img.format else ""
            if (
                img_format
                and img_format != file_extension
                and not (file_extension == "jpg" and img_format == "jpeg")
            ):
                st.warning(
                    f"⚠️ Image format ({img_format}) doesn't match extension ({file_extension})"
                )

        # Reset file pointer for later use
        if hasattr(uploaded_file, "seek"):
            uploaded_file.seek(original_position)

        return True

    except OSError as e:
        st.error(f"❌ Cannot read image file: {e}")
        return False
    except Exception as e:
        st.error(f"❌ Invalid image file: {e}")
        return False


def safe_create_directory(path: Path) -> bool:
    """Safely create directory with proper error handling."""
    try:
        path.mkdir(parents=True, exist_ok=True)
        return True
    except (OSError, PermissionError) as e:
        st.error(f"Failed to create directory: {e}")
        return False


# Configure page
st.set_page_config(
    page_title="Ollama Chat",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for maximum readability in dark theme
st.markdown(
    """
<style>
    /* FORÇA texto branco em TODAS as mensagens de chat */
    div[data-testid="stChatMessageContent"] {
        color: #ffffff !important;
    }
    
    div[data-testid="stChatMessageContent"] * {
        color: #ffffff !important;
    }
    
    div[data-testid="stChatMessageContent"] p {
        color: #ffffff !important;
    }
    
    div[data-testid="stChatMessageContent"] div {
        color: #ffffff !important;
    }
    
    div[data-testid="stChatMessageContent"] span {
        color: #ffffff !important;
    }
    
    /* Força cores específicas para elementos markdown */
    .st-emotion-cache-1w7qfeb {
        color: #ffffff !important;
    }
    
    .st-emotion-cache-1w7qfeb * {
        color: #ffffff !important;
    }
    
    .st-emotion-cache-1w7qfeb p {
        color: #ffffff !important;
        margin-bottom: 1rem !important;
    }
    
    .st-emotion-cache-1w7qfeb strong {
        color: #ffffff !important;
        font-weight: bold !important;
    }
    
    .st-emotion-cache-1w7qfeb em {
        color: #ffffff !important;
        font-style: italic !important;
    }
    
    .st-emotion-cache-1w7qfeb h1,
    .st-emotion-cache-1w7qfeb h2,
    .st-emotion-cache-1w7qfeb h3,
    .st-emotion-cache-1w7qfeb h4,
    .st-emotion-cache-1w7qfeb h5,
    .st-emotion-cache-1w7qfeb h6 {
        color: #ffffff !important;
    }
    
    .st-emotion-cache-1w7qfeb ul,
    .st-emotion-cache-1w7qfeb ol {
        color: #ffffff !important;
    }
    
    .st-emotion-cache-1w7qfeb li {
        color: #ffffff !important;
    }
    
    /* Containers das mensagens com melhor contraste */
    .st-emotion-cache-1mph9ef {
        background-color: rgba(30, 35, 45, 0.95) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
        border-radius: 12px !important;
        padding: 20px !important;
        margin: 12px 0 !important;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3) !important;
    }
    
    /* Mensagens do usuário - azul */
    .st-emotion-cache-1mph9ef:has([data-testid="user-message"]) {
        background-color: rgba(59, 130, 246, 0.25) !important;
        border: 1px solid rgba(59, 130, 246, 0.5) !important;
        border-left: 4px solid rgba(59, 130, 246, 0.8) !important;
    }
    
    /* Mensagens do assistente - verde */
    .st-emotion-cache-1mph9ef:has([data-testid="assistant-message"]) {
        background-color: rgba(34, 197, 94, 0.25) !important;
        border: 1px solid rgba(34, 197, 94, 0.5) !important;
        border-left: 4px solid rgba(34, 197, 94, 0.8) !important;
    }
    
    /* Blocos de código com contraste máximo */
    .st-emotion-cache-1w7qfeb pre {
        background-color: rgba(0, 0, 0, 0.8) !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        color: #ffffff !important;
        padding: 16px !important;
        border-radius: 8px !important;
        overflow-x: auto !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        font-size: 0.9em !important;
        line-height: 1.4 !important;
    }
    
    .st-emotion-cache-1w7qfeb pre * {
        color: #ffffff !important;
    }
    
    .st-emotion-cache-1w7qfeb code {
        background-color: rgba(0, 0, 0, 0.6) !important;
        color: #ffffff !important;
        padding: 2px 6px !important;
        border-radius: 4px !important;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }
    
    /* Qualquer elemento que contenha texto */
    [data-testid="stChatMessageContent"] > div > div {
        color: #ffffff !important;
    }
    
    /* Aplicar em qualquer elemento com texto */
    .st-emotion-cache-* {
        color: #ffffff !important;
    }
    
    /* Sidebar melhorada */
    .st-emotion-cache-16txtl3 {
        background-color: rgba(15, 20, 30, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Área de input melhorada */
    .st-emotion-cache-1f3w014 {
        background-color: rgba(20, 25, 35, 0.95) !important;
        border-top: 1px solid rgba(255, 255, 255, 0.15) !important;
    }
    
    /* Input de chat */
    .stChatInput textarea {
        background-color: rgba(40, 45, 55, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
    }
    
    .stChatInput textarea:focus {
        border-color: rgba(59, 130, 246, 0.6) !important;
        box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2) !important;
    }
    
    /* Botões aprimorados */
    .stButton > button {
        background-color: rgba(59, 130, 246, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(59, 130, 246, 0.7) !important;
        border-radius: 8px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
        padding: 8px 16px !important;
    }
    
    .stButton > button:hover {
        background-color: rgba(59, 130, 246, 1) !important;
        border: 1px solid rgba(59, 130, 246, 0.9) !important;
        transform: translateY(-1px) !important;
        box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3) !important;
    }
    
    /* Selectbox melhorado */
    .stSelectbox select {
        background-color: rgba(40, 45, 55, 0.9) !important;
        color: #ffffff !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 6px !important;
    }
    
    /* Notificações e alertas */
    .stInfo {
        background-color: rgba(59, 130, 246, 0.15) !important;
        border: 1px solid rgba(59, 130, 246, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .stSuccess {
        background-color: rgba(34, 197, 94, 0.15) !important;
        border: 1px solid rgba(34, 197, 94, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .stWarning {
        background-color: rgba(245, 158, 11, 0.15) !important;
        border: 1px solid rgba(245, 158, 11, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    .stError {
        background-color: rgba(239, 68, 68, 0.15) !important;
        border: 1px solid rgba(239, 68, 68, 0.4) !important;
        color: #ffffff !important;
        border-radius: 8px !important;
    }
    
    /* Melhorar upload de arquivos */
    .stFileUploader section {
        background-color: rgba(40, 45, 55, 0.8) !important;
        border: 2px dashed rgba(255, 255, 255, 0.4) !important;
        border-radius: 10px !important;
        color: #ffffff !important;
    }
    
    /* Scrollbar personalizada */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(15, 20, 30, 0.6);
        border-radius: 6px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.25);
        border-radius: 6px;
        border: 2px solid rgba(15, 20, 30, 0.6);
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.4);
    }
    
    ::-webkit-scrollbar-corner {
        background: rgba(15, 20, 30, 0.6);
    }
</style>
""",
    unsafe_allow_html=True,
)

# Chat history persistence with security validation
CHAT_HISTORY_DIR = Path.cwd() / ".ollama_chat_history"
if not safe_create_directory(CHAT_HISTORY_DIR):
    st.error("Failed to initialize chat history directory")
    st.stop()


def save_chat_history(messages: list[dict], session_id: str) -> None:
    """Save chat history to file with security validation."""
    if not validate_session_id(session_id):
        st.error("Invalid session ID")
        return

    history_file = CHAT_HISTORY_DIR / f"chat_{session_id}.json"
    chat_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "messages": messages,
        "message_count": len(messages),
    }
    try:
        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)
    except (OSError, PermissionError) as e:
        st.warning(f"Could not save chat history: {e}")


def load_chat_history(session_id: str) -> list[dict]:
    """Load chat history from file."""
    history_file = CHAT_HISTORY_DIR / f"chat_{session_id}.json"
    if history_file.exists():
        try:
            with open(history_file, encoding="utf-8") as f:
                chat_data = json.load(f)
                return chat_data.get("messages", [])
        except (OSError, json.JSONDecodeError) as e:
            st.warning(f"Could not load chat history: {e}")
    return []


def get_chat_sessions() -> list[str]:
    """Get list of available chat sessions."""
    try:
        sessions = []
        for file in CHAT_HISTORY_DIR.glob("chat_*.json"):
            session_id = file.stem.replace("chat_", "")
            sessions.append(session_id)
        return sorted(sessions, reverse=True)
    except OSError:
        return []


def get_context_summary(messages: list[dict]) -> str:
    """Generate a summary of the conversation context."""
    if not messages:
        return "No conversation history"

    user_messages = [msg for msg in messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]

    return f"Messages: {len(messages)} | User: {len(user_messages)} | Assistant: {len(assistant_messages)}"


def setup_ollama_gpu() -> bool:
    """Configure Ollama for GPU usage."""
    try:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        os.environ["OLLAMA_GPU"] = "1"
    except OSError:
        return False
    else:
        return True


@st.cache_resource
def get_ollama_client():
    """Initialize and cache Ollama client."""
    setup_ollama_gpu()
    return ollama.Client()


def get_available_models():
    """Get list of available Ollama models."""
    try:
        client = get_ollama_client()
        models_response = client.list()

        # Handle ollama._types.ListResponse object
        if hasattr(models_response, "models"):
            models_list = models_response.models
        elif isinstance(models_response, dict) and "models" in models_response:
            models_list = models_response["models"]
        else:
            models_list = models_response

        # Extract model names safely
        model_names = []
        for model in models_list:
            if hasattr(model, "model"):
                # For ollama Model objects, use .model attribute
                model_names.append(model.model)
            elif isinstance(model, dict):
                # Try different possible keys for model name
                name = model.get("name") or model.get("model") or model.get("id")
                if name:
                    model_names.append(name)
            elif isinstance(model, str):
                model_names.append(model)

        return model_names

    except ollama.ResponseError as e:
        st.error(f"Error fetching models: {e!s}")
        return []
    except Exception as e:
        st.error(f"Unexpected error fetching models: {e!s}")
        return []


def stream_ollama_response(
    client, model: str, messages: list[dict], temperature: float = 0.7
):
    """Stream response from Ollama."""
    try:
        # Prepare messages for Ollama API
        api_messages = []
        for msg in messages:
            ollama_msg = {"role": msg["role"], "content": msg["content"]}

            # Add images if present (for vision models)
            if msg.get("images"):
                ollama_msg["images"] = msg["images"]

            api_messages.append(ollama_msg)

        response = client.chat(
            model=model,
            messages=api_messages,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": 1000,
                "top_p": 0.9,
            },
        )

        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]

    except ollama.ResponseError as e:
        yield f"Error: {e!s}"


def encode_image_to_base64(image_file) -> str:
    """Convert uploaded image to base64 string with improved error handling."""
    if image_file is None:
        return ""

    try:
        # Ensure we're at the beginning of the file
        image_file.seek(0)

        # Read the image file and convert to base64
        image_bytes = image_file.read()

        # Verify we actually read some data
        if not image_bytes:
            st.error("Error: Empty file or failed to read image data")
            return ""

        # Encode to base64
        base64_string = base64.b64encode(image_bytes).decode("utf-8")

        # Reset file pointer for potential future use
        image_file.seek(0)

        return base64_string

    except OSError as e:
        st.error(f"Error reading image file: {e}")
        return ""
    except UnicodeDecodeError as e:
        st.error(f"Error encoding image to base64: {e}")
        return ""
    except Exception as e:
        st.error(f"Unexpected error processing image: {e}")
        return ""


def is_vision_model(model_name: str) -> bool:
    """Check if the model supports vision/images."""
    vision_keywords = ["vision", "vl", "visual", "llava", "qwen2-vl", "qwen2.5-vl"]
    return any(keyword in model_name.lower() for keyword in vision_keywords)


def display_message_with_images(message: dict):
    """Display a message that may contain images."""
    # Display text content
    if message.get("content"):
        st.markdown(message["content"])

    # Display images if present
    if message.get("images"):
        for i, img_data in enumerate(message["images"]):
            if isinstance(img_data, str):
                # If it's a base64 string, decode and display
                try:
                    img_bytes = base64.b64decode(img_data)
                    st.image(
                        img_bytes, caption=f"Image {i + 1}", use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error displaying image {i + 1}: {e}")
            else:
                # If it's already an image object
                st.image(img_data, caption=f"Image {i + 1}", use_container_width=True)


def resize_image(image: Image) -> Image:
    """Redimensionar imagem para largura e altura máximas, mantendo a proporção."""
    try:
        # Obter tamanho original
        original_width, original_height = image.size

        # Calcular a nova largura e altura mantendo a proporção
        if original_width > original_height:
            new_width = MAX_IMAGE_WIDTH
            new_height = int((MAX_IMAGE_WIDTH / original_width) * original_height)
        else:
            new_height = MAX_IMAGE_HEIGHT
            new_width = int((MAX_IMAGE_HEIGHT / original_height) * original_width)

        # Redimensionar a imagem
        resized_image = image.resize((new_width, new_height), Image.LANCZOS)

        return resized_image

    except Exception as e:
        st.error(f"Error resizing image: {e}")
        return image  # Retornar a imagem original em caso de erro


def optimize_image_for_vision(image_file) -> str:
    """Redimensiona e otimiza imagem para melhorar performance dos modelos de visão."""
    if image_file is None:
        return ""

    try:
        # Ensure we're at the beginning of the file
        image_file.seek(0)
        
        # Open image with PIL
        with Image.open(image_file) as img:
            # Convert to RGB if necessary (for consistency)
            if img.mode in ("RGBA", "LA", "P"):
                # Convert to RGB to avoid issues with transparency
                rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                rgb_img.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                img = rgb_img
            elif img.mode != "RGB":
                img = img.convert("RGB")
            
            # Get original dimensions
            original_width, original_height = img.size
            
            # Calculate new dimensions maintaining aspect ratio
            if original_width > MAX_IMAGE_WIDTH or original_height > MAX_IMAGE_HEIGHT:
                # Calculate scaling factor
                width_ratio = MAX_IMAGE_WIDTH / original_width
                height_ratio = MAX_IMAGE_HEIGHT / original_height
                scale_factor = min(width_ratio, height_ratio)
                
                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)
                
                # Resize image with high quality resampling
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                st.info(f"📏 Image resized from {original_width}x{original_height} to {new_width}x{new_height} for better performance")
            
            # Save optimized image to bytes
            img_byte_array = BytesIO()
            img.save(img_byte_array, format="JPEG", quality=IMAGE_QUALITY, optimize=True)
            img_bytes = img_byte_array.getvalue()
            
            # Calculate size reduction
            image_file.seek(0)
            original_size = len(image_file.read())
            new_size = len(img_bytes)
            reduction_percent = ((original_size - new_size) / original_size) * 100
            
            if reduction_percent > 0:
                st.success(f"🗜️ Image optimized: {original_size//1024}KB → {new_size//1024}KB ({reduction_percent:.1f}% smaller)")
            
            # Encode to base64
            base64_string = base64.b64encode(img_bytes).decode("utf-8")
            return base64_string

    except Exception as e:
        st.error(f"Error optimizing image: {e}")
        # Fallback to original encoding method
        return encode_image_to_base64(image_file)


def main():
    st.title("🤖 Ollama Chat Interface")
    st.markdown("Chat with your local Ollama models")

    # Sidebar for model selection and settings
    with st.sidebar:
        st.header("⚙️ Settings")

        # Model selection
        models = get_available_models()
        if not models:
            st.error("No Ollama models found. Please install models first.")
            st.code("ollama pull llama3.2:1b")
            return

        selected_model = st.selectbox(
            "Select Model", models, help="Choose an Ollama model to chat with"
        )

        # Image optimization setting
        st.markdown("---")
        st.subheader("🖼️ Image Optimization")
        optimize_images = st.checkbox(
            "Auto-optimize images for faster processing",
            value=OPTIMIZE_IMAGES,
            help="Automatically resize and compress images to improve model performance"
        )
        
        if optimize_images:
            st.info(f"📏 Max size: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}px | Quality: {IMAGE_QUALITY}%")
        else:
            st.info("🔧 Images will be sent without optimization")

        # Vision model indicator
        if selected_model and is_vision_model(selected_model):
            st.success("🔍 Vision model - supports images!")
        elif selected_model:
            st.info("💬 Text-only model")

        # Image upload section - MOVED TO SIDEBAR
        st.markdown("---")
        st.subheader("📷 Image Upload")

        # Initialize uploaded_images in session state
        if "uploaded_images" not in st.session_state:
            st.session_state.uploaded_images = []

        if selected_model and is_vision_model(selected_model):
            uploaded_files = st.file_uploader(
                "Upload images for analysis (max 200MB each)",
                type=["png", "jpg", "jpeg", "gif", "bmp"],
                accept_multiple_files=True,
                help="Upload images for the AI to analyze. "
                "Supported formats: PNG, JPG, JPEG, GIF, BMP",
                key="sidebar_image_uploader",
            )

            if uploaded_files:
                # Clear previous images and encode new ones
                st.session_state.uploaded_images = []

                # Validate all files before processing
                valid_files = []
                for i, uploaded_file in enumerate(uploaded_files):
                    st.write(f"🔍 Validating file {i + 1}: {uploaded_file.name}")
                    if sanitize_file_upload(uploaded_file):
                        valid_files.append(uploaded_file)
                        st.success(f"✅ File {i + 1} validated successfully")
                    else:
                        st.error(
                            f"❌ File {i + 1} validation failed: {uploaded_file.name}"
                        )

                if not valid_files:
                    st.error(
                        "❌ No valid files to process. Please check file requirements:"
                    )
                    st.info(
                        "📋 Requirements: PNG, JPG, JPEG, GIF, or BMP format, max 200MB"
                    )
                else:
                    st.success(f"✅ {len(valid_files)} valid image(s) ready for upload")

                    # Display image previews in sidebar
                    for i, uploaded_file in enumerate(valid_files):
                        try:
                            # Display small preview
                            uploaded_file.seek(0)  # Reset pointer before opening
                            image = Image.open(uploaded_file)
                            st.image(
                                image,
                                caption=f"Image {i + 1}: {uploaded_file.name}",
                                width=150,
                            )

                            # Reset file pointer and optimize/encode
                            uploaded_file.seek(0)
                            if optimize_images:
                                base64_image = optimize_image_for_vision(uploaded_file)
                            else:
                                base64_image = encode_image_to_base64(uploaded_file)
                            if base64_image:
                                st.session_state.uploaded_images.append(base64_image)
                        except Exception as e:
                            st.error(f"❌ Error processing {uploaded_file.name}: {e!s}")

                # Clear images button
                if st.button("🗑️ Clear Images", key="clear_images"):
                    st.session_state.uploaded_images = []
                    st.rerun()

            elif st.session_state.uploaded_images:
                st.info(
                    f"📎 {len(st.session_state.uploaded_images)} image(s) from previous upload"
                )
                if st.button("🗑️ Clear Images", key="clear_images_alt"):
                    st.session_state.uploaded_images = []
                    st.rerun()
        else:
            if st.session_state.uploaded_images:
                st.session_state.uploaded_images = []  # Clear images when switching to non-vision model
            st.info("💡 Select a vision model to upload images")

        # Temperature setting
        temperature = st.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Controls randomness of responses",
        )

        # System prompt
        system_prompt = st.text_area(
            "System Prompt (Optional)",
            placeholder="Enter a system prompt to guide the model's behavior...",
            help="Set the model's personality or behavior",
        )

        # Clear chat button
        if st.button("🗑️ Clear Chat", type="secondary"):
            st.session_state.messages = []
            st.rerun()

        # Session management
        st.markdown("---")
        st.subheader("📂 Session Management")

        # Show current session info
        if hasattr(st.session_state, "current_session"):
            st.info(f"📝 Current Session: {st.session_state.current_session}")

        # Load previous sessions
        sessions = get_chat_sessions()
        if sessions:
            st.write("**Previous Sessions:**")
            selected_session = st.selectbox(
                "Load Session",
                [""] + sessions,
                index=0,
                help="Select a previous chat session to continue",
                format_func=lambda x: "Select a session..." if x == "" else f"📅 {x}",
            )

            # Load session when selected
            if selected_session and selected_session != st.session_state.get(
                "current_session"
            ):
                loaded_messages = load_chat_history(selected_session)
                if loaded_messages:
                    st.session_state.messages = loaded_messages
                    st.session_state.current_session = selected_session
                    st.success(f"✅ Loaded session: {selected_session}")
                    st.rerun()

                # Display session context
                if st.session_state.messages:
                    context_summary = get_context_summary(st.session_state.messages)
                    st.markdown(f"**Session Context:** {context_summary}")
        else:
            st.info("No previous sessions found")

        # New session
        st.markdown("---")
        if st.button("🆕 Start New Session", type="primary"):
            # Save current session if it has messages
            if st.session_state.messages and hasattr(
                st.session_state, "current_session"
            ):
                save_chat_history(
                    st.session_state.messages, st.session_state.current_session
                )

            # Start new session
            st.session_state.messages = []
            st.session_state.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.session_state.uploaded_images = []  # Clear images too
            st.success("🎉 New session started!")
            st.rerun()

        # Model info
        st.markdown("---")
        st.markdown(f"**Current Model:** `{selected_model}`")

        # GPU status
        if "CUDA_VISIBLE_DEVICES" in os.environ:
            st.success("🚀 GPU Enabled")
        else:
            st.info("💻 CPU Mode")

    # Initialize chat history and session
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Initialize current session with timestamp
    if "current_session" not in st.session_state:
        st.session_state.current_session = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Auto-save existing conversation when there are messages
    if st.session_state.messages and hasattr(st.session_state, "current_session"):
        save_chat_history(st.session_state.messages, st.session_state.current_session)

    # Add system prompt to messages if provided
    messages_for_api = []
    if system_prompt.strip():
        enhanced_system_prompt = (
            system_prompt
            + "\n\nYou are having a conversation with the user. You have access to the full conversation history and should reference previous parts of the conversation when relevant. Always maintain context awareness throughout the conversation."
        )
        messages_for_api.append({"role": "system", "content": enhanced_system_prompt})

    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_message_with_images(message)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Get uploaded images from sidebar
        uploaded_images = st.session_state.get("uploaded_images", [])

        # Check if model supports vision when images are uploaded
        if uploaded_images and not is_vision_model(selected_model):
            st.error(
                "⚠️ Images uploaded but selected model doesn't support vision. Please select a vision model (e.g., qwen2.5-vl:7b, llava, etc.)"
            )
            st.stop()

        # Prepare user message
        user_message = {"role": "user", "content": prompt}

        # Add images if any were uploaded
        if uploaded_images:
            user_message["images"] = uploaded_images
            st.success(f"✅ Added {len(uploaded_images)} image(s) to message")

        # Add user message to chat history
        st.session_state.messages.append(user_message)

        # Display user message
        with st.chat_message("user"):
            display_message_with_images(user_message)

        # Prepare messages for API - Include FULL conversation history
        api_messages = messages_for_api.copy()

        # Add all previous messages as context (properly formatted for vision)
        for msg in st.session_state.messages:
            formatted_msg = {"role": msg["role"], "content": msg["content"]}
            # Add images if present
            if msg.get("images"):
                formatted_msg["images"] = msg["images"]

            api_messages.append(formatted_msg)

        # Enhanced context information
        context_info = f"💬 Using {len(api_messages)} messages as context"
        if len(st.session_state.messages) > 0:
            context_info += f" | History: {len(st.session_state.messages)} msgs"
        if system_prompt.strip():
            context_info += " | System prompt included"

        st.info(context_info)

        # Debug option to show what's being sent to the model
        with st.expander("🔍 Debug: View context being sent to model", expanded=False):
            st.write("**Messages being sent to Ollama:**")
            for i, msg in enumerate(api_messages):
                role_emoji = (
                    "🤖"
                    if msg["role"] == "system"
                    else "👤"
                    if msg["role"] == "user"
                    else "🤖"
                )
                st.write(
                    f"{i + 1}. {role_emoji} **{msg['role'].title()}:** {msg['content'][:100]}{'...' if len(msg['content']) > 100 else ''}"
                )
                if msg.get("images"):
                    st.write(f"   📸 Images: {len(msg['images'])}")

            st.write(f"**Total context size:** {len(api_messages)} messages")
            st.write(f"**Current session:** {st.session_state.current_session}")

            # Show conversation summary
            user_msgs = [m for m in st.session_state.messages if m["role"] == "user"]
            assistant_msgs = [
                m for m in st.session_state.messages if m["role"] == "assistant"
            ]
            st.write(
                f"**Conversation stats:** {len(user_msgs)} user messages, {len(assistant_msgs)} assistant responses"
            )

        # Generate and display assistant response
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""

            try:
                client = get_ollama_client()

                # Show typing indicator with context info
                with st.spinner(
                    f"Thinking with {len(api_messages)} messages context..."
                ):
                    for chunk in stream_ollama_response(
                        client, selected_model, api_messages, temperature
                    ):
                        full_response += chunk
                        message_placeholder.markdown(full_response + "▌")

                # Final response without cursor
                message_placeholder.markdown(full_response)

            except ollama.ResponseError as e:
                error_msg = f"Error: {e!s}"
                message_placeholder.error(error_msg)
                full_response = error_msg

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # Clear uploaded images after sending message
        if uploaded_images:
            st.session_state.uploaded_images = []

        # Auto-save after each exchange
        if hasattr(st.session_state, "current_session"):
            save_chat_history(
                st.session_state.messages, st.session_state.current_session
            )


if __name__ == "__main__":
    main()
