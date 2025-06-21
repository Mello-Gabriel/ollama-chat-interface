"""Configuration constants for the Ollama Chat Interface."""

import re

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

# Display constants
PREVIEW_LENGTH = 100  # Length for message preview in debug
