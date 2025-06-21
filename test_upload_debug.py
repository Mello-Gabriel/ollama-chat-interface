#!/usr/bin/env python3
"""Teste específico para depurar problemas de upload de imagem."""

import io

from PIL import Image

from chat_app import encode_image_to_base64, sanitize_file_upload


class MockStreamlitFile:
    """Mock do arquivo do Streamlit para teste."""

    def __init__(self, name, data, content_type=None):
        self.name = name
        self.data = data
        self.content_type = content_type
        self.size = len(data)
        self._position = 0

    def read(self, size=-1):
        if size == -1:
            result = self.data[self._position :]
            self._position = len(self.data)
        else:
            result = self.data[self._position : self._position + size]
            self._position = min(self._position + size, len(self.data))
        return result

    def seek(self, position):
        self._position = max(0, min(position, len(self.data)))

    def tell(self):
        return self._position

    def getvalue(self):
        return self.data


def create_test_image():
    """Cria uma imagem PNG válida para teste."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()


def test_upload_validation():
    """Testa a validação de upload sem Streamlit."""
    print("🔍 Testando validação de upload sem interface Streamlit...")

    # Criar imagem de teste
    png_data = create_test_image()
    print(f"✅ Imagem PNG criada: {len(png_data)} bytes")

    # Testar arquivo válido
    valid_file = MockStreamlitFile("test.png", png_data)
    print(f"\n📁 Testando arquivo válido: {valid_file.name}")
    print(f"   Tamanho: {valid_file.size} bytes")

    # Capturar saída de erro (simulando st.error)
    import sys
    from io import StringIO

    # Redirecionar stderr para capturar mensagens de erro
    old_stderr = sys.stderr
    sys.stderr = error_capture = StringIO()

    try:
        # Monkey patch st.error para não gerar erro
        import streamlit as st

        original_error = st.error
        st.error = lambda msg: print(f"ST_ERROR: {msg}")

        result = sanitize_file_upload(valid_file)
        print(f"   Resultado da validação: {result}")

        if result:
            # Testar encoding
            valid_file.seek(0)
            base64_result = encode_image_to_base64(valid_file)
            if base64_result:
                print(
                    f"✅ Encoding para base64 bem-sucedido: {len(base64_result)} caracteres"
                )
            else:
                print("❌ Falha no encoding para base64")

        # Restaurar st.error
        st.error = original_error

    except ImportError:
        print("⚠️ Streamlit não disponível, testando apenas lógica básica")

        # Testar validação básica sem streamlit
        if valid_file.name and valid_file.size > 0:
            extension = valid_file.name.split(".")[-1].lower()
            if extension in ["png", "jpg", "jpeg", "gif", "bmp"]:
                print("✅ Extensão válida")

                # Testar se é uma imagem válida
                try:
                    valid_file.seek(0)
                    img = Image.open(io.BytesIO(valid_file.data))
                    print(f"✅ Imagem válida: {img.format} {img.size}")
                except Exception as e:
                    print(f"❌ Erro ao abrir imagem: {e}")

    finally:
        sys.stderr = old_stderr


def test_common_issues():
    """Testa problemas comuns de upload."""
    print("\n🐛 Testando problemas comuns...")

    # 1. Arquivo sem extensão
    print("\n1. Arquivo sem extensão:")
    no_ext_file = MockStreamlitFile("arquivo_sem_extensao", b"fake data")
    try:
        import streamlit as st

        st.error = lambda msg: print(f"   ERROR: {msg}")
        result = sanitize_file_upload(no_ext_file)
        print(f"   Resultado: {result}")
    except ImportError:
        print("   Streamlit não disponível")

    # 2. Arquivo muito grande
    print("\n2. Arquivo muito grande:")
    large_data = b"x" * (300 * 1024 * 1024)  # 300MB
    large_file = MockStreamlitFile("large.png", large_data)
    try:
        import streamlit as st

        st.error = lambda msg: print(f"   ERROR: {msg}")
        result = sanitize_file_upload(large_file)
        print(f"   Resultado: {result}")
    except ImportError:
        print("   Streamlit não disponível")

    # 3. Arquivo corrompido
    print("\n3. Arquivo corrompido:")
    corrupt_file = MockStreamlitFile("corrupt.png", b"not an image")
    try:
        import streamlit as st

        st.error = lambda msg: print(f"   ERROR: {msg}")
        result = sanitize_file_upload(corrupt_file)
        print(f"   Resultado: {result}")
    except ImportError:
        print("   Streamlit não disponível")


if __name__ == "__main__":
    print("🚀 Iniciando teste de depuração de upload...")
    test_upload_validation()
    test_common_issues()
    print("\n✅ Teste concluído!")
