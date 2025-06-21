"""Image processing utilities for the Ollama Chat Interface."""

import base64
from io import BytesIO
from typing import Any

import streamlit as st
from PIL import Image

from src.config import IMAGE_QUALITY, MAX_IMAGE_HEIGHT, MAX_IMAGE_WIDTH


def encode_image_to_base64(image_file: Any) -> str:
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


def optimize_image_for_vision(image_file: Any) -> str:
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
                    rgba_img = img.convert("RGBA")
                    rgb_img.paste(
                        rgba_img,
                        mask=rgba_img.split()[-1] if rgba_img.mode in ("RGBA", "LA") else None
                    )
                else:
                    rgb_img.paste(
                        img, 
                        mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
                    )
                processed_img = rgb_img
            elif img.mode != "RGB":
                processed_img = img.convert("RGB")
            else:
                processed_img = img.copy()

            # Get original dimensions
            original_width, original_height = processed_img.size

            # Calculate new dimensions maintaining aspect ratio
            if original_width > MAX_IMAGE_WIDTH or original_height > MAX_IMAGE_HEIGHT:
                # Calculate scaling factor
                width_ratio = MAX_IMAGE_WIDTH / original_width
                height_ratio = MAX_IMAGE_HEIGHT / original_height
                scale_factor = min(width_ratio, height_ratio)

                new_width = int(original_width * scale_factor)
                new_height = int(original_height * scale_factor)

                # Resize image with high quality resampling
                processed_img = processed_img.resize(
                    (new_width, new_height), 
                    Image.Resampling.LANCZOS
                )

                st.info(
                    f"📏 Image resized from {original_width}x{original_height} "
                    f"to {new_width}x{new_height} for better performance"
                )

            # Save optimized image to bytes
            img_byte_array = BytesIO()
            processed_img.save(
                img_byte_array, 
                format="JPEG", 
                quality=IMAGE_QUALITY, 
                optimize=True
            )
            img_bytes = img_byte_array.getvalue()

            # Calculate size reduction
            image_file.seek(0)
            original_size = len(image_file.read())
            new_size = len(img_bytes)
            reduction_percent = ((original_size - new_size) / original_size) * 100

            if reduction_percent > 0:
                st.success(
                    f"🗜️ Image optimized: {original_size//1024}KB → "
                    f"{new_size//1024}KB ({reduction_percent:.1f}% smaller)"
                )

            # Encode to base64
            return base64.b64encode(img_bytes).decode("utf-8")

    except Exception as e:
        st.error(f"Error optimizing image: {e}")
        # Fallback to original encoding method
        return encode_image_to_base64(image_file)


def is_vision_model(model_name: str) -> bool:
    """Check if the model supports vision/images."""
    if not model_name:
        return False
    vision_keywords = ["vision", "vl", "visual", "llava", "qwen2-vl", "qwen2.5-vl"]
    return any(keyword in model_name.lower() for keyword in vision_keywords)


def display_message_with_images(message: dict[str, Any]) -> None:
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
                        img_bytes, 
                        caption=f"Image {i + 1}", 
                        use_container_width=True
                    )
                except Exception as e:
                    st.error(f"Error displaying image {i + 1}: {e}")
            else:
                # If it's already an image object
                st.image(
                    img_data, 
                    caption=f"Image {i + 1}", 
                    use_container_width=True
                )
