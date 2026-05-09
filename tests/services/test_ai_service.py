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

    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    async def test_generate_description_terminal_error(self, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        # Non-retryable error
        mock_error = Exception("Fatal error")
        mock_error.status_code = 400
        mock_client.chat.completions.create.side_effect = mock_error
        
        service = AIService()
        desc = await service.generate_description("prompt", "response")
        
        assert desc == "Nova conversa"

    @pytest.mark.asyncio
    @patch("src.services.ai_service.AsyncOpenAI")
    async def test_generate_response_stream_chunk_error(self, mock_async_openai):
        mock_client = AsyncMock()
        mock_async_openai.return_value = mock_client
        
        mock_chunk = MagicMock()
        # This will cause _process_chunk to fail if we mock it to raise
        
        async def mock_generator():
            yield mock_chunk

        mock_client.chat.completions.create.return_value = mock_generator()

        service = AIService()
        with patch.object(service, '_process_chunk', side_effect=Exception("Process error")):
            generator = service.generate_response_stream([{"role": "user", "content": "Hi"}])
            with pytest.raises(Exception) as excinfo:
                async for _ in generator:
                    pass
            assert "Process error" in str(excinfo.value)

    def test_is_retryable(self):
        service = AIService()
        
        # Test with status_code attribute
        err1 = Exception("error")
        err1.status_code = 429
        assert service._is_retryable(err1) is True
        
        err2 = Exception("error")
        err2.status_code = 404
        assert service._is_retryable(err2) is False
        
        # Test with string matching
        assert service._is_retryable(Exception("Error 500: Internal Server Error")) is True
        assert service._is_retryable(Exception("Generic error")) is False

    def test_process_chunk_with_reasoning(self):
        service = AIService()
        
        mock_chunk = MagicMock()
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = "Thinking..."
        mock_chunk.choices[0].delta.reasoning = "I should say hello"
        
        result = service._process_chunk(mock_chunk)
        
        assert result["content"] == "Thinking..."
        assert result["reasoning"] == "I should say hello"

    def test_process_chunk_empty(self):
        service = AIService()
        
        mock_chunk = MagicMock()
        mock_chunk.choices = []
        assert service._process_chunk(mock_chunk) is None
        
        mock_chunk.choices = [MagicMock()]
        mock_chunk.choices[0].delta.content = None
        mock_chunk.choices[0].delta.reasoning = None
        assert service._process_chunk(mock_chunk) is None
