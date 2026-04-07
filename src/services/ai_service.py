import json
import google.generativeai as genai
from openai import OpenAI
from typing import Generator, List
from src.core.config import settings
from src.models.ai import AIModel, AIPersona

class AIService:
    def __init__(self):
        self.openrouter_client = OpenAI(
            base_url=settings.OPENROUTER_BASE_URL,
            api_key=settings.OPENROUTER_API_KEY,
        )
        if settings.GOOGLE_API_KEY:
            genai.configure(api_key=settings.GOOGLE_API_KEY)

    def generate_response_stream(
        self, 
        history: List[dict], 
        model: AIModel = AIModel.GEMINI_1_5_FLASH, 
        persona: AIPersona = AIPersona.ROTEIRISTA
    ) -> Generator[dict, None, None]:
        
        if model.provider == "gemini":
            yield from self._generate_google_stream(history, model, persona)
        else:
            yield from self._generate_openrouter_stream(history, model, persona)

    def _generate_openrouter_stream(
        self, 
        history: List[dict], 
        model: AIModel, 
        persona: AIPersona
    ) -> Generator[dict, None, None]:
        if not settings.OPENROUTER_API_KEY:
            yield {
                "role": "assistant",
                "content": "Erro: OPENROUTER_API_KEY não configurada no backend.",
                "reasoning": "",
            }
            return

        messages = [{"role": "system", "content": persona.value}] + history

        completion = self.openrouter_client.chat.completions.create(
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

    def _generate_google_stream(
        self, 
        history: List[dict], 
        model: AIModel, 
        persona: AIPersona
    ) -> Generator[dict, None, None]:
        if not settings.GOOGLE_API_KEY:
            yield {
                "role": "assistant",
                "content": "Erro: GOOGLE_API_KEY não configurada no backend.",
                "reasoning": "",
            }
            return
         
        google_history = []
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            google_history.append({"role": role, "parts": [msg["content"]]})

        gen_model = genai.GenerativeModel(
            model_name=model.value,
            system_instruction=persona.value
        )

        chat = gen_model.start_chat(history=google_history[:-1] if google_history else [])
        
        last_msg = google_history[-1]["parts"][0] if google_history else ""
        
        try:
            response = chat.send_message(last_msg, stream=True)

            for chunk in response:
                try:
                    response_chunk = {
                        "role": "assistant",
                        "content": chunk.text,
                        "reasoning": "",
                    }
                    yield response_chunk
                except Exception:
                    continue
        except Exception as e:
            yield {
                "role": "assistant",
                "content": f"Erro ao chamar Google AI Studio: {str(e)}",
                "reasoning": "",
            }

ai_service = AIService()
