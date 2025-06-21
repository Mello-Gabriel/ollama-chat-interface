"""Main entry point for the Ollama Chat Interface.

A secure Streamlit application for chatting with local Ollama models.

Security features:
- Input validation and sanitization
- File upload restrictions
- Session ID validation
- Safe directory operations
"""

import sys
from datetime import UTC, datetime
from pathlib import Path

import streamlit as st

# Add src to path for imports
sys.path.append(str(Path(__file__).parent / "src"))

from src.ui.components import (
    load_css,
    render_chat_messages,
    render_debug_info,
    render_sidebar,
)
from src.utils.chat_history import (
    initialize_chat_history_dir,
    save_chat_history,
)
from src.utils.image_processing import (
    display_message_with_images,
    is_vision_model,
)
from src.utils.ollama_client import (
    get_ollama_client,
    stream_ollama_response,
)


def initialize_app() -> None:
    """Initialize the Streamlit application."""
    # Configure page
    st.set_page_config(
        page_title="Ollama Chat",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    # Load custom CSS
    load_css()

    # Initialize chat history directory
    if not initialize_chat_history_dir():
        st.error("Failed to initialize chat history directory")
        st.stop()


def initialize_session_state() -> None:
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "current_session" not in st.session_state:
        st.session_state.current_session = datetime.now(UTC).strftime("%Y%m%d_%H%M%S")

    if "uploaded_images" not in st.session_state:
        st.session_state.uploaded_images = []


def prepare_api_messages(system_prompt: str) -> list[dict]:
    """Prepare messages for the Ollama API."""
    messages_for_api = []
    
    if system_prompt.strip():
        enhanced_system_prompt = (
            system_prompt
            + "\n\nYou are having a conversation with the user. "
            "You have access to the full conversation history and should "
            "reference previous parts of the conversation when relevant. "
            "Always maintain context awareness throughout the conversation."
        )
        messages_for_api.append({"role": "system", "content": enhanced_system_prompt})

    # Add all previous messages as context (properly formatted for vision)
    for msg in st.session_state.messages:
        formatted_msg = {"role": msg["role"], "content": msg["content"]}
        # Add images if present
        if msg.get("images"):
            formatted_msg["images"] = msg["images"]
        messages_for_api.append(formatted_msg)

    return messages_for_api


def handle_user_input(prompt: str, selected_model: str) -> dict:
    """Process user input and create user message."""
    # Get uploaded images from sidebar
    uploaded_images = st.session_state.get("uploaded_images", [])

    # Check if model supports vision when images are uploaded
    if uploaded_images and not is_vision_model(selected_model):
        st.error(
            "⚠️ Images uploaded but selected model doesn't support vision. "
            "Please select a vision model (e.g., qwen2.5-vl:7b, llava, etc.)"
        )
        st.stop()

    # Prepare user message
    user_message = {"role": "user", "content": prompt}

    # Add images if any were uploaded
    if uploaded_images:
        user_message["images"] = uploaded_images
        st.success(f"✅ Added {len(uploaded_images)} image(s) to message")

    return user_message


def generate_response(
    client, selected_model: str, api_messages: list, temperature: float
) -> str:
    """Generate response from Ollama."""
    message_placeholder = st.empty()
    full_response = ""

    try:
        # Show typing indicator with context info
        with st.spinner(f"Thinking with {len(api_messages)} messages context..."):
            for chunk in stream_ollama_response(
                client, selected_model, api_messages, temperature
            ):
                full_response += chunk
                message_placeholder.markdown(full_response + "▌")

        # Final response without cursor
        message_placeholder.markdown(full_response)

    except Exception as e:
        error_msg = f"Error: {e!s}"
        message_placeholder.error(error_msg)
        full_response = error_msg

    return full_response


def main() -> None:
    """Main application function."""
    # Initialize the application
    initialize_app()
    initialize_session_state()

    # Render UI
    st.title("🤖 Ollama Chat Interface")
    st.markdown("Chat with your local Ollama models")

    # Render sidebar and get settings
    selected_model, temperature, system_prompt, optimize_images = render_sidebar()

    # Auto-save existing conversation when there are messages
    if st.session_state.messages and hasattr(st.session_state, "current_session"):
        save_chat_history(st.session_state.messages, st.session_state.current_session)

    # Prepare API messages
    api_messages = prepare_api_messages(system_prompt)

    # Display chat messages
    render_chat_messages()

    # Enhanced context information and debug info
    render_debug_info(api_messages, system_prompt)

    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Handle user input
        user_message = handle_user_input(prompt, selected_model)

        # Add user message to chat history
        st.session_state.messages.append(user_message)

        # Display user message
        with st.chat_message("user"):
            display_message_with_images(user_message)

        # Update API messages with the new user message
        api_messages = prepare_api_messages(system_prompt)

        # Generate and display assistant response
        with st.chat_message("assistant"):
            client = get_ollama_client()
            full_response = generate_response(
                client, selected_model, api_messages, temperature
            )

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )

        # Clear uploaded images after sending message
        if st.session_state.get("uploaded_images"):
            st.session_state.uploaded_images = []

        # Auto-save after each exchange
        if hasattr(st.session_state, "current_session"):
            save_chat_history(
                st.session_state.messages, st.session_state.current_session
            )


if __name__ == "__main__":
    main()
