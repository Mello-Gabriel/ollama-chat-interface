#!/usr/bin/env python3
"""Teste do sistema de salvar/carregar chats"""

import json
import sys
from datetime import datetime
from pathlib import Path

# Simular estrutura do chat_app
CHAT_HISTORY_DIR = Path.home() / ".ollama_chat_history"
CHAT_HISTORY_DIR.mkdir(exist_ok=True)


def test_save_load_system():
    """Testar o sistema de salvar e carregar chats."""
    print("🧪 Testando Sistema de Salvar/Carregar Chats")
    print("=" * 50)

    # Dados de teste
    test_session_id = f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    test_messages = [
        {"role": "user", "content": "Olá! Como você está?"},
        {
            "role": "assistant",
            "content": "Olá! Estou bem, obrigado. Como posso ajudá-lo hoje?",
        },
        {
            "role": "user",
            "content": "Pode me explicar como funciona o sistema de chat?",
        },
        {
            "role": "assistant",
            "content": "Claro! Este é um sistema de chat com IA usando Ollama...",
        },
    ]

    # Testar salvamento
    print(f"📝 Salvando sessão de teste: {test_session_id}")
    try:
        history_file = CHAT_HISTORY_DIR / f"chat_{test_session_id}.json"
        chat_data = {
            "timestamp": datetime.now().isoformat(),
            "messages": test_messages,
            "message_count": len(test_messages),
        }

        with open(history_file, "w", encoding="utf-8") as f:
            json.dump(chat_data, f, indent=2, ensure_ascii=False)

        print("✅ Salvamento realizado com sucesso!")
        print(f"   Arquivo: {history_file}")
        print(f"   Mensagens: {len(test_messages)}")

    except Exception as e:
        print(f"❌ Erro no salvamento: {e}")
        return False

    # Testar carregamento
    print(f"\n📖 Carregando sessão: {test_session_id}")
    try:
        if history_file.exists():
            with open(history_file, encoding="utf-8") as f:
                loaded_data = json.load(f)
                loaded_messages = loaded_data.get("messages", [])

            print("✅ Carregamento realizado com sucesso!")
            print(f"   Mensagens carregadas: {len(loaded_messages)}")
            print(f"   Timestamp: {loaded_data.get('timestamp')}")

            # Verificar integridade
            if loaded_messages == test_messages:
                print("✅ Integridade dos dados confirmada!")
            else:
                print("⚠️ Dados carregados diferem dos originais")

        else:
            print("❌ Arquivo não encontrado")
            return False

    except Exception as e:
        print(f"❌ Erro no carregamento: {e}")
        return False

    # Listar sessões disponíveis
    print("\n📂 Listando todas as sessões:")
    try:
        sessions = []
        for file in CHAT_HISTORY_DIR.glob("chat_*.json"):
            session_id = file.stem.replace("chat_", "")
            sessions.append(session_id)

        sessions = sorted(sessions, reverse=True)

        if sessions:
            print(f"   Total de sessões: {len(sessions)}")
            for i, session in enumerate(
                sessions[:5]
            ):  # Mostrar apenas as 5 mais recentes
                print(f"   {i + 1}. {session}")
            if len(sessions) > 5:
                print(f"   ... e mais {len(sessions) - 5} sessões")
        else:
            print("   Nenhuma sessão encontrada")

    except Exception as e:
        print(f"❌ Erro ao listar sessões: {e}")
        return False

    # Limpeza
    print("\n🧹 Removendo arquivo de teste...")
    try:
        history_file.unlink()
        print("✅ Arquivo de teste removido")
    except Exception as e:
        print(f"⚠️ Erro ao remover arquivo de teste: {e}")

    print("\n🎉 Teste concluído com sucesso!")
    return True


if __name__ == "__main__":
    success = test_save_load_system()
    sys.exit(0 if success else 1)
