import json
import logging
import asyncio
from openai import AsyncOpenAI, APIError, InternalServerError
from typing import AsyncGenerator, List, Optional
from src.core.config import settings
from src.models.ai import AIModel, AIPersona

logger = logging.getLogger(__name__)

class AIService:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )

    def _is_retryable(self, e: Exception) -> bool:
        status_code = getattr(e, "status_code", None)
        if status_code in [429, 500, 502, 503, 504]:
            return True
        err_str = str(e)
        return any(code in err_str for code in ["500", "502", "503", "504", "429"])

    def _process_chunk(self, chunk) -> Optional[dict]:
        if not chunk.choices:
            return None
            
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

        return response_chunk if updated else None

    async def generate_response_stream(
        self, 
        history: List[dict], 
        model: AIModel = AIModel.GEMINI_3_FLASH, 
        persona: AIPersona = AIPersona.ROTEIRISTA
    ) -> AsyncGenerator[dict, None]:
        
        messages = [{"role": "system", "content": persona.value}] + history
        max_retries = 3
        retry_delay = 1

        for attempt in range(max_retries):
            started_yielding = False
            try:
                completion = await self.client.chat.completions.create(
                    model=model.value,
                    messages=messages,
                    stream=True
                )

                async for chunk in completion:
                    try:
                        processed = self._process_chunk(chunk)
                        if processed:
                            started_yielding = True
                            yield processed
                    except Exception as e:
                        logger.warning(f"Error processing stream chunk: {e}")
                        raise e
                
                return

            except Exception as e:
                if started_yielding:
                    logger.error(f"Mid-stream error in generate_response_stream: {e}")
                    raise e

                if self._is_retryable(e) and attempt < max_retries - 1:
                    logger.warning(f"Retryable error in generate_response_stream (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"Streaming error in generate_response_stream: {e}")
                    raise e

    async def generate_description(self, prompt: str, response: str) -> str:
        messages = [
            {"role": "system", "content": "Você é um assistente encarregado de resumir conversas. Crie uma descrição curta (máximo 10 palavras) para a conversa baseada no primeiro prompt do usuário e na resposta da IA."},
            {"role": "user", "content": f"Prompt: {prompt}\nResposta: {response}"}
        ]
        
        max_retries = 3
        retry_delay = 1
        
        for attempt in range(max_retries):
            try:
                completion = await self.client.chat.completions.create(
                    model=AIModel.GEMMA_4.value,
                    messages=messages,
                    max_tokens=50
                )
                return completion.choices[0].message.content.strip().replace('"', '')
            except Exception as e:
                if self._is_retryable(e) and attempt < max_retries - 1:
                    logger.warning(f"Retryable error in generate_description (attempt {attempt + 1}): {e}")
                    await asyncio.sleep(retry_delay * (attempt + 1))
                    continue
                else:
                    logger.error(f"Error generating description: {e}")
                    return "Nova conversa"

ai_service = AIService()
