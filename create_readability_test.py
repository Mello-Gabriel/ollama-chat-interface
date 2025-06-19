#!/usr/bin/env python3
"""Script para testar as melhorias de legibilidade do tema."""

import json
from datetime import datetime
from pathlib import Path

# Chat history directory
CHAT_HISTORY_DIR = Path.home() / ".ollama_chat_history"


def create_readability_test_session():
    """Cria uma sessão de teste com vários tipos de conteúdo para testar legibilidade."""
    messages = [
        {
            "role": "user",
            "content": "Pode me explicar diferentes tipos de conteúdo que podemos usar no chat?",
        },
        {
            "role": "assistant",
            "content": "Claro! Posso mostrar vários tipos de conteúdo:\n\n**Texto simples:** Este é um exemplo de texto normal com boa legibilidade.\n\n**Código Python:**\n```python\ndef hello_world():\n    print('Olá, mundo!')\n    return 'Hello World'\n```\n\n**Lista numerada:**\n1. Primeiro item\n2. Segundo item\n3. Terceiro item\n\n**Lista com marcadores:**\n- Item A\n- Item B\n- Item C\n\n**Código inline:** Use `print()` para imprimir valores.\n\n**Texto com formatação:** *itálico*, **negrito**, e ~~riscado~~.",
        },
        {"role": "user", "content": "Agora mostre um exemplo de código mais complexo"},
        {
            "role": "assistant",
            "content": "Aqui está um exemplo mais complexo:\n\n```python\nclass ChatApp:\n    def __init__(self, model_name: str):\n        self.model = model_name\n        self.history = []\n    \n    def send_message(self, message: str) -> str:\n        \"\"\"Envia uma mensagem e retorna a resposta.\"\"\"\n        self.history.append({\n            'role': 'user',\n            'content': message,\n            'timestamp': datetime.now()\n        })\n        \n        # Simular resposta\n        response = f\"Processando: {message}\"\n        self.history.append({\n            'role': 'assistant', \n            'content': response,\n            'timestamp': datetime.now()\n        })\n        \n        return response\n```\n\n**Explicação:**\n- A classe `ChatApp` gerencia conversas\n- Método `send_message()` processa mensagens\n- Histórico é armazenado em lista de dicionários\n- Timestamps são adicionados automaticamente",
        },
        {
            "role": "user",
            "content": "Como fica o contraste do texto agora? É mais fácil de ler?",
        },
        {
            "role": "assistant",
            "content": "**Melhorias de Contraste Implementadas:**\n\n✅ **Fundo das mensagens:** Cores mais escuras com transparência\n✅ **Texto:** Branco puro (#ffffff) para máximo contraste\n✅ **Bordas:** Sutis com transparência para definir as áreas\n✅ **Código:** Fundo mais escuro para destacar do texto normal\n✅ **Botões:** Azul com bom contraste e efeitos hover\n\n**Diferenças por tipo de mensagem:**\n- **Usuário:** Fundo azul translúcido\n- **Assistente:** Fundo verde translúcido  \n- **Código:** Fundo preto com transparência\n\n**Resultado:** Texto muito mais legível mantendo o tema escuro elegante!",
        },
    ]

    # Criar sessão de teste
    session_id = f"readability_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    history_file = CHAT_HISTORY_DIR / f"chat_{session_id}.json"
    chat_data = {
        "timestamp": datetime.now().isoformat(),
        "messages": messages,
        "message_count": len(messages),
    }

    with open(history_file, "w", encoding="utf-8") as f:
        json.dump(chat_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Sessão de teste de legibilidade criada: {session_id}")
    print(f"📁 Arquivo: {history_file}")
    print(f"💬 {len(messages)} mensagens com vários tipos de conteúdo")
    print("\n🎨 Teste as melhorias de legibilidade na aplicação!")


if __name__ == "__main__":
    create_readability_test_session()
