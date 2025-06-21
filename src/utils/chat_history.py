"""Chat history management utilities."""

import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import streamlit as st

from src.utils.security import safe_create_directory, validate_session_id

# Chat history persistence with security validation
CHAT_HISTORY_DIR = Path.cwd() / ".ollama_chat_history"


def initialize_chat_history_dir() -> bool:
    """Initialize chat history directory."""
    return safe_create_directory(CHAT_HISTORY_DIR)


def save_chat_history(messages: list[dict[str, Any]], session_id: str) -> None:
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


def load_chat_history(session_id: str) -> list[dict[str, Any]]:
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


def get_context_summary(messages: list[dict[str, Any]]) -> str:
    """Generate a summary of the conversation context."""
    if not messages:
        return "No conversation history"

    user_messages = [msg for msg in messages if msg["role"] == "user"]
    assistant_messages = [msg for msg in messages if msg["role"] == "assistant"]

    return (
        f"Messages: {len(messages)} | "
        f"User: {len(user_messages)} | "
        f"Assistant: {len(assistant_messages)}"
    )
