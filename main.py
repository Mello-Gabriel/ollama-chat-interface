from ollama import ChatResponse, chat

image_path = "/home/mello/projects/sort_files/1.png"

response: ChatResponse = chat(
    model="qwen2.5vl:7b",
    messages=[
        {
            "role": "user",
            "content": "What is this image? Please describe it.",
            "images": [image_path],
        }
    ],
)


print(response.message.content)
