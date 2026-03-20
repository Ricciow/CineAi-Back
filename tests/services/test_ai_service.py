from unittest.mock import MagicMock, patch
from src.services.ai_service import AIService
from src.models.ai import AIModel, AIPersona

class TestAIService:
    @patch("src.services.ai_service.OpenAI")
    def test_generate_response_stream_success(self, mock_openai):
        # Mock client and its behavior
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        # Mock completion chunks
        mock_chunk1 = MagicMock()
        mock_chunk1.choices[0].delta.content = "Hello "
        mock_chunk1.choices[0].delta.reasoning = None
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices[0].delta.content = "world!"
        mock_chunk2.choices[0].delta.reasoning = None
        
        mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]

        # Since AIService is instantiated as a global object, we might need to recreate it for tests
        # or patch the client on the existing instance.
        service = AIService()
        history = [{"role": "user", "content": "Hi"}]
        
        generator = service.generate_response_stream(
            history=history,
            model=AIModel.DEEPSEEK,
            persona=AIPersona.ROTEIRISTA
        )
        
        responses = list(generator)
        
        assert len(responses) == 2
        assert responses[0]["content"] == "Hello "
        assert responses[1]["content"] == "world!"
        mock_client.chat.completions.create.assert_called_once()

    @patch("src.services.ai_service.OpenAI")
    def test_generate_response_stream_with_reasoning(self, mock_openai):
        # Mock client and its behavior
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        
        mock_chunk1 = MagicMock()
        mock_chunk1.choices[0].delta.content = None
        mock_chunk1.choices[0].delta.reasoning = "Thinking..."
        
        mock_chunk2 = MagicMock()
        mock_chunk2.choices[0].delta.content = "Final answer"
        mock_chunk2.choices[0].delta.reasoning = None
        
        mock_client.chat.completions.create.return_value = [mock_chunk1, mock_chunk2]

        service = AIService()
        history = [{"role": "user", "content": "Hi"}]
        
        generator = service.generate_response_stream(history=history)
        responses = list(generator)
        
        assert responses[0]["reasoning"] == "Thinking..."
        assert responses[1]["content"] == "Final answer"
