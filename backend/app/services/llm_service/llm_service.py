from typing import List, Dict
import os
from openai import AsyncOpenAI
from app.core.settings import get_settings
from app.core.logger import get_logger

logger = get_logger(__name__)

settings = get_settings()

class LLMService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

        self.model = settings.OPENROUTER_MODEL

    async def generate_reply(
        self,
        summary: str,
        messages: List[Dict],
        user_input: str,
        user_info: str
    ) -> str:
        """
        Generates AI response using OpenRouter GPT model (Asynchronous)
        """

        # ---- Build prompt messages ----
        prompt_messages = []

        # 1️⃣ System memory / summary
        # Note: Left-aligned to avoid leading whitespace tokens in the prompt
        prompt_messages.append({
            "role": "system",
            "content": f"""You are an Disha AI healthcare assistant.

PATIENT MEMORY SUMMARY:
{summary}
and user general information and medications history:
{user_info}

Give safe, clear, and concise guidance and don't ans unneccessary questions apart from health."""
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

        # ---- Call OpenRouter (Awaited) ----
        logger.info(f"Generating AI reply using model: {self.model}")
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=prompt_messages,
            temperature=0.3,
        )

        logger.info("AI reply generated successfully")
        return response.choices[0].message.content.strip()
