import json
import logging
import asyncio
from openai import AsyncOpenAI, APIError, InternalServerError
from typing import AsyncGenerator, List
from src.core.config import settings
from src.models.ai import AIModel, AIPersona

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

    async def generate_response_stream(
        self, 
        history: List[dict], 
        model: AIModel = AIModel.GEMINI_3_FLASH, 
        persona: AIPersona = AIPersona.ROTEIRISTA
    ) -> AsyncGenerator[dict, None]:
        
        messages = [{"role": "system", "content": persona.value}] + history

        try:
            completion = await self.client.chat.completions.create(
                model=model.value,
                messages=messages,
                stream=True
            )

            async for chunk in completion:
                try:
                    if not chunk.choices:
                        continue
                        
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
                except Exception as e:
                    logger.warning(f"Error processing stream chunk: {e}")
                    raise e
        except Exception as e:
            logger.error(f"Streaming error in generate_response_stream: {e}")
            raise e

ai_service = AIService()
