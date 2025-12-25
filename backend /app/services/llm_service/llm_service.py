from typing import List, Dict


class LLMService:
    def generate_reply(
        self,
        summary: str,
        messages: List[Dict],
        user_input: str
    ) -> str:
        # Later replace with OpenAI / Gemini / Claude
        return f"AI reply to: {user_input}"
