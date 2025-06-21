"""Security and validation utilities for the Ollama Chat Interface."""

from pathlib import Path

import streamlit as st
from PIL import Image

from ..config import (
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE,
    MAX_SESSION_ID_LENGTH,
    SESSION_ID_PATTERN,
)


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
            f"❌ Invalid file type '{file_extension}'. "
            f"Allowed: {', '.join(ALLOWED_IMAGE_TYPES)}"
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
                    f"⚠️ Image format ({img_format}) doesn't match "
                    f"extension ({file_extension})"
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
