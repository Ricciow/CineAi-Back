import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from src.services.ai_service import AIService
from src.models.ai import AIModel, AIPersona

class TestAIService:
    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    async def test_generate_response_stream_success(self, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        mock_chunk1 = MagicMock()
        mock_chunk1.choices = [MagicMock()]
        mock_chunk1.choices[0].delta.content = "Hello "
        mock_chunk1.choices[0].delta.reasoning = None
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices = [MagicMock()]
        mock_chunk2.choices[0].delta.content = "world!"
        mock_chunk2.choices[0].delta.reasoning = None
        
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

    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    @patch("src.services.ai_service.asyncio.sleep", return_value=None)
    async def test_generate_response_stream_retry_success(self, mock_sleep, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        # Create a mock error that looks like a provider error
        mock_error = Exception("Error code: 502 - Provider returned error")
        mock_error.status_code = 502
        
        # Mock first call fails, second succeeds
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Success"
        mock_chunk.choices[0].delta.reasoning = None
        
        async def mock_generator_success():
            yield mock_chunk

        mock_client.chat.completions.create.side_effect = [mock_error, mock_generator_success()]

        service = AIService()
        generator = service.generate_response_stream([{"role": "user", "content": "Hi"}])
        
        responses = []
        async for resp in generator:
            responses.append(resp)
            
        assert len(responses) == 1
        assert responses[0]["content"] == "Success"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once()

    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    @patch("src.services.ai_service.asyncio.sleep", return_value=None)
    async def test_generate_response_stream_mid_stream_no_retry(self, mock_sleep, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Part 1"
        mock_chunk.choices[0].delta.reasoning = None
        
        mock_error = Exception("Error code: 502 - Mid-stream error")
        mock_error.status_code = 502
        
        async def mock_generator_mid_fail():
            yield mock_chunk
            raise mock_error

        mock_client.chat.completions.create.return_value = mock_generator_mid_fail()

        service = AIService()
        generator = service.generate_response_stream([{"role": "user", "content": "Hi"}])
        
        responses = []
        with pytest.raises(Exception) as excinfo:
            async for resp in generator:
                responses.append(resp)
        
        assert "502" in str(excinfo.value)
        assert len(responses) == 1
        assert responses[0]["content"] == "Part 1"
        assert mock_client.chat.completions.create.call_count == 1
        mock_sleep.assert_not_called()

    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    @patch("src.services.ai_service.asyncio.sleep", return_value=None)
    async def test_generate_description_retry(self, mock_sleep, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        mock_error = Exception("Error code: 502")
        mock_error.status_code = 502
        
        mock_completion = MagicMock()
        mock_completion.choices = [MagicMock()]
        mock_completion.choices[0].message.content = "Description"
        
        mock_client.chat.completions.create.side_effect = [mock_error, mock_completion]
        
        service = AIService()
        desc = await service.generate_description("prompt", "response")
        
        assert desc == "Description"
        assert mock_client.chat.completions.create.call_count == 2
        mock_sleep.assert_called_once()
