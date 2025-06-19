#!/usr/bin/env python3
"""Test script for chat save/load functionality."""

import json
from datetime import datetime
from pathlib import Path

# Import the chat functions
from chat_app import get_chat_sessions, load_chat_history, save_chat_history


def test_chat_save_load():
    """Test saving and loading chat history."""
    print("🧪 Testing chat save/load functionality...")

    # Create test messages
    test_messages = [
        {"role": "user", "content": "Hello, how are you?"},
        {
            "role": "assistant",
            "content": "I'm doing well, thank you! How can I help you today?",
        },
        {"role": "user", "content": "Can you help me with Python programming?"},
        {
            "role": "assistant",
            "content": "Of course! I'd be happy to help you with Python programming. What specific topic would you like to explore?",
        },
    ]

    # Use a test session ID
    test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    print(f"📝 Saving test session: {test_session_id}")

    # Test saving
    try:
        save_chat_history(test_messages, test_session_id)
        print("✅ Chat history saved successfully")
    except Exception as e:
        print(f"❌ Error saving chat history: {e}")
        return False

    # Test loading
    try:
        loaded_messages = load_chat_history(test_session_id)
        print(f"📖 Loaded {len(loaded_messages)} messages")

        # Verify content
        if loaded_messages == test_messages:
            print("✅ Loaded messages match original messages")
        else:
            print("❌ Loaded messages don't match original messages")
            print("Original:", test_messages)
            print("Loaded:", loaded_messages)
            return False

    except Exception as e:
        print(f"❌ Error loading chat history: {e}")
        return False

    # Test getting sessions
    try:
        sessions = get_chat_sessions()
        print(f"📂 Found {len(sessions)} chat sessions")

        if test_session_id in sessions:
            print("✅ Test session found in session list")
        else:
            print("❌ Test session not found in session list")
            print("Available sessions:", sessions)

    except Exception as e:
        print(f"❌ Error getting chat sessions: {e}")
        return False

    # Check the actual file
    chat_dir = Path.home() / ".ollama_chat_history"
    test_file = chat_dir / f"chat_{test_session_id}.json"

    if test_file.exists():
        print(f"✅ Chat file exists: {test_file}")

        # Read and display file content
        try:
            with open(test_file) as f:
                file_content = json.load(f)
                print(f"📄 File content keys: {list(file_content.keys())}")
                print(
                    f"📊 Message count in file: {file_content.get('message_count', 'unknown')}"
                )
                print(f"🕒 Timestamp: {file_content.get('timestamp', 'unknown')}")
        except Exception as e:
            print(f"❌ Error reading file: {e}")

    else:
        print(f"❌ Chat file does not exist: {test_file}")
        return False

    print("\n✅ All tests passed! Chat save/load functionality is working correctly.")
    return True


if __name__ == "__main__":
    success = test_chat_save_load()
    exit(0 if success else 1)
