from typing import List, Dict
import os
from openai import OpenAI


class LLMService:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key="testing"
        )

        self.model = "openai/gpt-4o-mini"  # fast + cheap + good for chat

    def generate_reply(
        self,
        summary: str,
        messages: List[Dict],
        user_input: str
    ) -> str:
        """
        Generates AI response using OpenRouter GPT model
        """

        # ---- Build prompt messages ----
        prompt_messages = []

        # 1️⃣ System memory / summary
        if summary:
            prompt_messages.append({
                "role": "system",
                "content": f"""
You are an Disha AI healthcare assistant.

PATIENT MEMORY SUMMARY:
{summary}

Give safe, clear, and concise guidance.
"""
            })

        # 2️⃣ Previous conversation (last 3–5 messages ideally)
        for msg in messages:
            prompt_messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })

        # 3️⃣ Current user input
        prompt_messages.append({
            "role": "user",
            "content": user_input
        })

        # ---- Call OpenRouter ----
        response = self.client.chat.completions.create(
            model=self.model,
            messages=prompt_messages,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()
