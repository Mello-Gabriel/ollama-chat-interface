"""Ollama integration utilities."""

import os
from collections.abc import Generator
from typing import Any

import ollama
import streamlit as st


def setup_ollama_gpu() -> bool:
    """Configure Ollama for GPU usage."""
    try:
        os.environ["CUDA_VISIBLE_DEVICES"] = "0"
        os.environ["OLLAMA_GPU"] = "1"
        return True
    except OSError:
        return False


@st.cache_resource
def get_ollama_client() -> ollama.Client:
    """Initialize and cache Ollama client."""
    setup_ollama_gpu()
    return ollama.Client()


def get_available_models() -> list[str]:
    """Get list of available Ollama models."""
    try:
        client = get_ollama_client()
        models_response = client.list()

        # Handle ollama._types.ListResponse object
        if hasattr(models_response, "models"):
            models_list = models_response.models
        elif isinstance(models_response, dict) and "models" in models_response:
            models_list = models_response["models"]
        else:
            models_list = models_response

        # Extract model names safely
        model_names = []
        for model in models_list:
            if hasattr(model, "model"):
                # For ollama Model objects, use .model attribute
                model_names.append(model.model)
            elif isinstance(model, dict):
                # Try different possible keys for model name
                name = model.get("name") or model.get("model") or model.get("id")
                if name:
                    model_names.append(name)
            elif isinstance(model, str):
                model_names.append(model)

        return model_names

    except ollama.ResponseError as e:
        st.error(f"Error fetching models: {e!s}")
        return []
    except Exception as e:
        st.error(f"Unexpected error fetching models: {e!s}")
        return []


def stream_ollama_response(
    client: ollama.Client,
    model: str,
    messages: list[dict[str, Any]],
    temperature: float = 0.7,
) -> Generator[str, None, None]:
    """Stream response from Ollama."""
    try:
        # Prepare messages for Ollama API
        api_messages = []
        for msg in messages:
            ollama_msg = {"role": msg["role"], "content": msg["content"]}

            # Add images if present (for vision models)
            if msg.get("images"):
                ollama_msg["images"] = msg["images"]

            api_messages.append(ollama_msg)

        response = client.chat(
            model=model,
            messages=api_messages,
            stream=True,
            options={
                "temperature": temperature,
                "num_predict": 1000,
                "top_p": 0.9,
            },
        )

        for chunk in response:
            if "message" in chunk and "content" in chunk["message"]:
                yield chunk["message"]["content"]

    except ollama.ResponseError as e:
        yield f"Error: {e!s}"
