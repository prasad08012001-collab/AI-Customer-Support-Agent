
from openai import OpenAI


# Connect to Local Ollama Server
client = OpenAI(
    base_url="http://localhost:11434/v1/",
    api_key="ollama"
)


# Generate AI Customer Support Reply
def generate_ai_response(user_message, chat_history=None):

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful customer support agent. "
                "Give polite, clear and short answers to customers. "
                "Use previous conversation messages as context. "
                "If you don't know something, don't invent an answer."
            )
        }
    ]

    # Add Previous Conversation History
    if chat_history:
        messages.extend(chat_history)
    else:
        messages.append({
            "role": "user",
            "content": user_message
        })

    # Send Request to Ollama
    response = client.chat.completions.create(
        model="qwen2.5:3b",
        messages=messages
    )

    return response.choices[0].message.content
