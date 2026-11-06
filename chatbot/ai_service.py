
import os
from openai import OpenAI


def generate_ai_response(message, chat_history=None):

    api_key = os.getenv("GROQ_API_KEY")

    if not api_key:
        raise ValueError("GROQ_API_KEY is missing from environment.")

    client = OpenAI(
        api_key=api_key,
        base_url="https://api.groq.com/openai/v1"
    )

    messages = [
        {
            "role": "system",
            "content": (
                "You are a helpful AI customer support assistant. "
                "Answer politely, clearly, and briefly. "
                "Help users with general customer support questions. "
                "Never invent order or ticket details. "
                "For private order or ticket information, "
                "ask the user to use the application's verification process."
            )
        }
    ]

    if chat_history:
        for item in chat_history[-10:]:
            role = item.get("role")
            content = item.get("content")

            if role in ["user", "assistant"] and content:
                messages.append({
                    "role": role,
                    "content": content
                })

    # Avoid adding the current message twice
    if not chat_history or not (
        chat_history[-1].get("role") == "user"
        and chat_history[-1].get("content") == message
    ):
        messages.append({
            "role": "user",
            "content": message
        })

    response = client.chat.completions.create(
        model=os.getenv("GROQ_MODEL", "openai/gpt-oss-20b"),
        messages=messages,
        temperature=0.5,
        max_completion_tokens=500
    )

    return response.choices[0].message.content.strip()
