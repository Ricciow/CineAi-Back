import json
from openai import OpenAI
from typing import Generator, List
from src.core.config import settings
from src.models.ai import AIModel, AIPersona

class AIService:
    def __init__(self):
        self.client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

    def generate_response_stream(
        self, 
        history: List[dict], 
        model: AIModel = AIModel.GEMINI_2_5_FLASH, 
        persona: AIPersona = AIPersona.ROTEIRISTA
    ) -> Generator[dict, None, None]:
        
        messages = [{"role": "system", "content": persona.value}] + history

        completion = self.client.chat.completions.create(
            model=model.value,
            messages=messages,
            stream=True
        )

        for chunk in completion:
            try:
                delta = chunk.choices[0].delta
                response_chunk = {
                    "role": "assistant",
                    "content": "",
                    "reasoning": "",
                }
                updated = False
                if hasattr(delta, 'content') and delta.content:
                    response_chunk["content"] = delta.content
                    updated = True
                if hasattr(delta, 'reasoning') and delta.reasoning:
                    response_chunk["reasoning"] = delta.reasoning
                    updated = True

                if updated:
                    yield response_chunk
            except Exception:
                continue

ai_service = AIService()
