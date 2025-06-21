#!/usr/bin/env python3
"""Teste simples das funções de upload"""

import io
import sys

from PIL import Image


# Simular streamlit para teste
class FakeStreamlit:
    @staticmethod
    def error(msg):
        print(f"ERROR: {msg}")

    @staticmethod
    def warning(msg):
        print(f"WARNING: {msg}")


# Adicionar caminho e substituir streamlit
sys.modules["streamlit"] = FakeStreamlit()

# Agora importar as funções
from chat_app import MAX_FILE_SIZE, sanitize_file_upload


def test_file_validation():
    """Teste das validações de arquivo."""
    print("🧪 Testando validações de upload de arquivos...")
    print(f"📏 Tamanho máximo configurado: {MAX_FILE_SIZE / (1024 * 1024):.0f}MB")

    # Classe para simular arquivo
    class FakeFile:
        def __init__(self, name, size, content=None):
            self.name = name
            self.size = size
            self.content = content or b"fake content"
            self.position = 0

        def read(self):
            return self.content

        def seek(self, pos):
            self.position = pos

    # Criar imagem PNG válida
    img = Image.new("RGB", (100, 100), color="red")
    img_bytes = io.BytesIO()
    img.save(img_bytes, format="PNG")
    img_content = img_bytes.getvalue()

    print(f"\n1. Testando arquivo PNG válido (tamanho: {len(img_content)} bytes):")
    fake_png = FakeFile("test.png", len(img_content), img_content)
    result1 = sanitize_file_upload(fake_png)
    print(f"   Resultado: {result1}")

    print(f"\n2. Testando arquivo muito grande ({MAX_FILE_SIZE + 1} bytes):")
    fake_large = FakeFile("large.png", MAX_FILE_SIZE + 1)
    result2 = sanitize_file_upload(fake_large)
    print(f"   Resultado: {result2}")

    print("\n3. Testando arquivo sem extensão:")
    fake_no_ext = FakeFile("noext", 1024)
    result3 = sanitize_file_upload(fake_no_ext)
    print(f"   Resultado: {result3}")

    print("\n4. Testando extensão inválida (.txt):")
    fake_txt = FakeFile("test.txt", 1024)
    result4 = sanitize_file_upload(fake_txt)
    print(f"   Resultado: {result4}")

    print("\n5. Testando arquivo None:")
    result5 = sanitize_file_upload(None)
    print(f"   Resultado: {result5}")

    print("\n✅ Testes de validação concluídos!")
    print(
        f"📊 Resultados: PNG válido: {result1}, Grande: {result2}, Sem ext: {result3}, TXT: {result4}, None: {result5}"
    )


if __name__ == "__main__":
    test_file_validation()
