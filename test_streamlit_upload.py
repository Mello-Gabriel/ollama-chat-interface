#!/usr/bin/env python3
"""Script para testar upload de imagem no Streamlit sem interface."""

import io

import streamlit as st
from PIL import Image

# Configurar o app sem interface gráfica
st.set_page_config(page_title="Teste", layout="wide")


def create_test_image():
    """Cria uma imagem de teste."""
    img = Image.new("RGB", (100, 100), color="red")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)
    return buffer


def test_streamlit_upload():
    """Testa o upload usando Streamlit."""
    st.write("🔍 Teste de Upload no Streamlit")

    # Criar imagem de teste
    test_image = create_test_image()
    test_data = test_image.getvalue()

    st.write(f"📏 Imagem criada: {len(test_data)} bytes")

    # Simular file uploader
    uploaded_file = st.file_uploader(
        "Teste de upload",
        type=["png", "jpg", "jpeg", "gif", "bmp"],
        help="Teste",
    )

    if uploaded_file is not None:
        st.write(f"✅ Arquivo carregado: {uploaded_file.name}")
        st.write(f"📏 Tamanho: {uploaded_file.size} bytes")

        # Tentar validação
        try:
            from chat_app import sanitize_file_upload

            result = sanitize_file_upload(uploaded_file)
            st.write(f"✅ Validação: {result}")
        except Exception as e:
            st.error(f"❌ Erro na validação: {e}")
    else:
        st.info("👆 Faça upload de uma imagem para testar")


if __name__ == "__main__":
    test_streamlit_upload()
