"""UI components for the Ollama Chat Interface."""

from datetime import datetime
from pathlib import Path

import streamlit as st
from PIL import Image

from src.config import (
    IMAGE_QUALITY,
    MAX_IMAGE_HEIGHT,
    MAX_IMAGE_WIDTH,
    OPTIMIZE_IMAGES,
    PREVIEW_LENGTH,
)
from src.utils.chat_history import (
    get_chat_sessions,
    get_context_summary,
    load_chat_history,
)
from src.utils.image_processing import (
    display_message_with_images,
    encode_image_to_base64,
    is_vision_model,
    optimize_image_for_vision,
)
from src.utils.ollama_client import get_available_models
from src.utils.security import sanitize_file_upload


def load_css() -> None:
    """Load custom CSS from external file."""
    css_file = Path("assets/styles.css")
    if css_file.exists():
        with open(css_file, encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def render_sidebar() -> tuple[str, float, str, bool]:
    """Render the sidebar with all controls."""
    with st.sidebar:
        st.header("⚙️ Settings")

        # Model selection
        models = get_available_models()
        if not models:
            st.error("No Ollama models found. Please install models first.")
            st.code("ollama pull llama3.2:1b")
            st.stop()

        selected_model = st.selectbox(
            "Select Model", models, help="Choose an Ollama model to chat with"
        )

        # Image optimization setting
        st.markdown("---")
        st.subheader("🖼️ Image Optimization")
        optimize_images = st.checkbox(
            "Auto-optimize images for faster processing",
            value=OPTIMIZE_IMAGES,
            help="Automatically resize and compress images to improve model performance",
        )

        if optimize_images:
            st.info(
                f"📏 Max size: {MAX_IMAGE_WIDTH}x{MAX_IMAGE_HEIGHT}px | "
                f"Quality: {IMAGE_QUALITY}%"
            )
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
                    f"📎 {len(st.session_state.uploaded_images)} "
                    "image(s) from previous upload"
                )
                if st.button("🗑️ Clear Images", key="clear_images_alt"):
                    st.session_state.uploaded_images = []
                    st.rerun()
        else:
            if st.session_state.uploaded_images:
                # Clear images when switching to non-vision model
                st.session_state.uploaded_images = []
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
                ["", *sessions],
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
                from src.utils.chat_history import save_chat_history

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
        import os

        if "CUDA_VISIBLE_DEVICES" in os.environ:
            st.success("🚀 GPU Enabled")
        else:
            st.info("💻 CPU Mode")

    return selected_model, temperature, system_prompt, optimize_images


def render_chat_messages() -> None:
    """Render all chat messages."""
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            display_message_with_images(message)


def render_debug_info(api_messages: list, system_prompt: str) -> None:
    """Render debug information about the conversation context."""
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
            content_preview = msg["content"][:PREVIEW_LENGTH]
            if len(msg["content"]) > PREVIEW_LENGTH:
                content_preview += "..."

            st.write(
                f"{i + 1}. {role_emoji} **{msg['role'].title()}:** {content_preview}"
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
            f"**Conversation stats:** {len(user_msgs)} user messages, "
            f"{len(assistant_msgs)} assistant responses"
        )
