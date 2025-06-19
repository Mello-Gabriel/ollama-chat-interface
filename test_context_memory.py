#!/usr/bin/env python3
"""Script para criar uma conversa de teste que demonstra o contexto funcionando."""

import json
from datetime import datetime
from pathlib import Path

# Chat history directory
CHAT_HISTORY_DIR = Path.home() / ".ollama_chat_history"

def create_context_test_session():
    """Cria uma sessão para testar se o contexto está funcionando."""
    
    messages = [
        {
            "role": "user",
            "content": "Olá! Meu nome é João e eu sou desenvolvedor Python. Pode me lembrar disso?"
        },
        {
            "role": "assistant", 
            "content": "Olá João! É um prazer conhecê-lo. Sim, vou me lembrar que você é desenvolvedor Python. Como posso ajudá-lo hoje com seus projetos de desenvolvimento?"
        },
        {
            "role": "user",
            "content": "Qual é o meu nome e profissão que eu acabei de te contar?"
        },
        {
            "role": "assistant",
            "content": "Você me disse que seu nome é João e que você é desenvolvedor Python. É isso mesmo!"
        },
        {
            "role": "user",
            "content": "Perfeito! Agora me diga: sobre o que estamos conversando desde o início?"
        },
        {
            "role": "assistant",
            "content": "Desde o início da nossa conversa, estamos falando sobre:\n\n1. **Sua apresentação:** Você se apresentou como João, desenvolvedor Python\n2. **Teste de memória:** Você pediu para eu me lembrar dessa informação\n3. **Verificação de contexto:** Você testou se eu lembrava do seu nome e profissão\n4. **Esta pergunta:** Agora você está perguntando sobre todo o contexto da conversa\n\nEssa conversa toda é basicamente um teste para verificar se estou mantendo o contexto e a continuidade da nossa interação. E pelo que posso ver, está funcionando perfeitamente!"
        }
    ]
    
    # Criar sessão de teste de contexto
    session_id = f"context_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    history_file = CHAT_HISTORY_DIR / f"chat_{session_id}.json"
    chat_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
        "message_count": len(messages),
    }
    
    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Sessão de teste de contexto criada: {session_id}")
    print(f"📁 Arquivo: {history_file}")
    print(f"💬 {len(messages)} mensagens demonstrando contexto funcionando")
    print("\n🧪 Use esta sessão para testar:")
    print("1. Carregue a sessão na aplicação")
    print("2. Pergunte: 'Qual é meu nome?' ou 'Do que estávamos falando?'")
    print("3. O modelo deve se lembrar do contexto anterior!")

if __name__ == "__main__":
    create_context_test_session()
