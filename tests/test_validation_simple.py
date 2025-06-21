#!/usr/bin/env python3
"""Teste simples para verificar se a função de validação está causando o erro 403."""

import base64
import io

from PIL import Image


def create_simple_png():
    """Cria uma imagem PNG simples como o arquivo 1.png."""
    # Criar uma imagem simples
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


class SimpleFile:
    """Simula um arquivo enviado pelo Streamlit."""

    def __init__(self, name, data):
        self.name = name
        self.data = data
        self.size = len(data)
        self.position = 0

    def read(self, size=-1):
        if size == -1:
            result = self.data[self.position :]
            self.position = len(self.data)
        else:
            result = self.data[self.position : self.position + size]
            self.position = min(self.position + size, len(self.data))
        return result

    def seek(self, position):
        self.position = max(0, min(position, len(self.data)))

    def tell(self):
        return self.position


def test_basic_validation():
    """Testa a validação básica de arquivo."""
    print("🔍 Testando validação básica...")

    # Criar arquivo de teste
    png_buffer = create_simple_png()
    png_data = png_buffer.getvalue()

    test_file = SimpleFile("1.png", png_data)

    print(f"📁 Arquivo criado: {test_file.name}")
    print(f"📏 Tamanho: {test_file.size} bytes")

    # Testar se é uma imagem válida
    try:
        test_file.seek(0)
        img = Image.open(io.BytesIO(test_file.data))
        print(f"✅ Imagem válida: {img.format} {img.size}")

        # Testar encoding para base64
        test_file.seek(0)
        base64_data = base64.b64encode(test_file.data).decode("utf-8")
        print(f"✅ Base64 encoding: {len(base64_data)} caracteres")

    except Exception as e:
        print(f"❌ Erro: {e}")


def test_extension_validation():
    """Testa validação de extensões."""
    print("\n🔍 Testando extensões...")

    extensions = ["png", "jpg", "jpeg", "gif", "bmp"]
    allowed_types = {"png", "jpg", "jpeg", "gif", "bmp"}

    for ext in extensions:
        if ext in allowed_types:
            print(f"✅ {ext}: permitido")
        else:
            print(f"❌ {ext}: rejeitado")


def test_size_limits():
    """Testa limites de tamanho."""
    print("\n🔍 Testando limites de tamanho...")

    max_size = 200 * 1024 * 1024  # 200MB

    # Arquivo pequeno
    small_data = b"x" * 1000  # 1KB
    print(
        f"📏 Arquivo pequeno (1KB): {'✅ OK' if len(small_data) <= max_size else '❌ Muito grande'}"
    )

    # Arquivo médio
    medium_data = b"x" * (10 * 1024 * 1024)  # 10MB
    print(
        f"📏 Arquivo médio (10MB): {'✅ OK' if len(medium_data) <= max_size else '❌ Muito grande'}"
    )

    # Arquivo grande
    # large_data = b"x" * (300 * 1024 * 1024)  # 300MB (comentado para não usar muita memória)
    print(
        f"📏 Arquivo grande (300MB): {'❌ Muito grande' if max_size < 300 * 1024 * 1024 else '✅ OK'}"
    )


if __name__ == "__main__":
    print("🚀 Iniciando testes de validação simples...")
    test_basic_validation()
    test_extension_validation()
    test_size_limits()
    print("\n✅ Testes concluídos!")
