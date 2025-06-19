#!/usr/bin/env python3
"""Create multiple test chat sessions to demonstrate functionality."""

import json
from datetime import datetime, timedelta
from pathlib import Path

# Chat history directory
CHAT_HISTORY_DIR = Path.home() / ".ollama_chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)


def create_test_session(session_id: str, messages: list[dict], days_ago: int = 0):
    """Create a test chat session with specific timestamp."""
    timestamp = datetime.now() - timedelta(days=days_ago)

    history_file = CHAT_HISTORY_DIR / f"chat_{session_id}.json"
    chat_data = {
        "timestamp": timestamp.isoformat(),
        "messages": messages,
        "message_count": len(messages),
    }

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Created session: {session_id} ({len(messages)} messages)")


# Create multiple test sessions
test_sessions = [
    {
        "id": "python_help_20250619_120000",
        "messages": [
            {"role": "user", "content": "Como criar uma lista em Python?"},
            {
                "role": "assistant",
                "content": "Para criar uma lista em Python, você pode usar colchetes:\n\n```python\nminha_lista = [1, 2, 3, 'texto', True]\n```",
            },
            {"role": "user", "content": "E como adicionar um item?"},
            {
                "role": "assistant",
                "content": "Use o método `append()` para adicionar um item ao final da lista:\n\n```python\nminha_lista.append('novo_item')\n```",
            },
        ],
        "days_ago": 1,
    },
    {
        "id": "web_development_20250618_140000",
        "messages": [
            {"role": "user", "content": "Qual a diferença entre HTML e CSS?"},
            {
                "role": "assistant",
                "content": "HTML é a linguagem de marcação que define a estrutura do conteúdo, enquanto CSS é usado para estilizar e formatar essa estrutura.",
            },
            {"role": "user", "content": "Pode dar um exemplo?"},
            {
                "role": "assistant",
                "content": "Claro! HTML:\n```html\n<h1>Título</h1>\n<p>Parágrafo</p>\n```\n\nCSS:\n```css\nh1 { color: blue; }\np { font-size: 16px; }\n```",
            },
        ],
        "days_ago": 2,
    },
    {
        "id": "ai_discussion_20250617_160000",
        "messages": [
            {"role": "user", "content": "O que você acha sobre o futuro da IA?"},
            {
                "role": "assistant",
                "content": "A IA tem potencial para transformar muitas áreas, desde automação até descobertas científicas. É importante desenvolvê-la de forma ética e responsável.",
            },
            {"role": "user", "content": "Quais são os principais desafios?"},
            {
                "role": "assistant",
                "content": "Os principais desafios incluem:\n1. Viés algorítmico\n2. Transparência e explicabilidade\n3. Privacidade dos dados\n4. Impacto no mercado de trabalho\n5. Segurança e confiabilidade",
            },
        ],
        "days_ago": 3,
    },
]

print("🧪 Creating test chat sessions...")
for session in test_sessions:
    create_test_session(session["id"], session["messages"], session["days_ago"])

print(f"\n📂 Chat sessions created in: {CHAT_HISTORY_DIR}")
print("🚀 Now you can test the session loading functionality in the Streamlit app!")
