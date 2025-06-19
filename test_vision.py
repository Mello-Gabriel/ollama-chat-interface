#!/usr/bin/env python3
"""Simple test script for vision models with Ollama"""

import ollama


def test_vision_model():
    """Test vision model with the existing image in the directory."""
    image_path = "/home/mello/projects/sort_files/1.png"

    try:
        # Initialize Ollama client
        client = ollama.Client()

        # Check if we have any vision models
        models_response = client.list()
        vision_models = []

        # Handle ollama._types.ListResponse object
        if hasattr(models_response, "models"):
            models_list = models_response.models
        elif isinstance(models_response, dict) and "models" in models_response:
            models_list = models_response["models"]
        else:
            models_list = models_response if isinstance(models_response, list) else []

        for model in models_list:
            # Safely get model name
            if hasattr(model, "model"):
                model_name = model.model
            elif isinstance(model, dict):
                model_name = model.get("name") or model.get("model") or model.get("id")
            else:
                model_name = str(model)

            if model_name and any(
                keyword in model_name.lower()
                for keyword in [
                    "vision",
                    "vl",
                    "visual",
                    "llava",
                    "qwen2-vl",
                    "qwen2.5-vl",
                ]
            ):
                vision_models.append(model_name)

        if not vision_models:
            print("❌ No vision models found. Please install a vision model:")
            print("   ollama pull qwen2.5-vl:7b")
            print("   ollama pull llava")
            return

        print(f"✅ Found vision models: {', '.join(vision_models)}")

        # Test with the first available vision model
        model_to_use = vision_models[0]
        print(f"🔍 Testing with model: {model_to_use}")

        response = client.chat(
            model=model_to_use,
            messages=[
                {
                    "role": "user",
                    "content": "What do you see in this image? Please describe it in detail.",
                    "images": [image_path],
                }
            ],
        )

        print(f"🤖 Response: {response['message']['content']}")

    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure Ollama is running and you have vision models installed.")


if __name__ == "__main__":
    test_vision_model()
