import os
from groq import Groq
from fastapi import HTTPException


def generate_llm_response(messages):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="LLM service unavailable: GROQ_API_KEY is not configured."
        )

    client = Groq(api_key=api_key)

    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=messages,
        temperature=0.6,
    )

    return completion.choices[0].message.content