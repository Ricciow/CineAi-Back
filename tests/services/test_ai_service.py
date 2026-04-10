import pytest
from unittest.mock import AsyncMock, patch
from src.services.ai_service import AIService
from src.models.ai import AIModel, AIPersona

class TestAIService:
    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    async def test_generate_response_stream_success(self, mock_async_openai):
        # Mock client and its behavior
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        # Mock completion chunks
        mock_chunk1 = AsyncMock()
        mock_chunk1.choices[0].delta.content = "Hello "
        mock_chunk1.choices[0].delta.reasoning = None
        
        mock_chunk2 = AsyncMock()
        mock_chunk2.choices[0].delta.content = "world!"
        mock_chunk2.choices[0].delta.reasoning = None
        
        # Async generators are a bit tricky to mock with AsyncMock in some versions
        async def mock_generator():
            yield mock_chunk1
            yield mock_chunk2

        mock_client.chat.completions.create.return_value = mock_generator()

        service = AIService()
        history = [{"role": "user", "content": "Hi"}]
        
        generator = service.generate_response_stream(
            history=history,
            model=AIModel.GEMINI_3_FLASH,
            persona=AIPersona.ROTEIRISTA
        )
        
        responses = []
        async for resp in generator:
            responses.append(resp)
        
        assert len(responses) == 2
        assert responses[0]["content"] == "Hello "
        assert responses[1]["content"] == "world!"
        mock_client.chat.completions.create.assert_called_once()
