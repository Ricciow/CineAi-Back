from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from src.api.deps import get_current_user_id

client = TestClient(app)

# Mock dependency
def override_get_current_user_id():
    return "60d5ecb54f1a2c001f8e4e1a"

app.dependency_overrides[get_current_user_id] = override_get_current_user_id

class TestConversationEndpoints:
    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_create_conversation(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.create.return_value = {
            "id": "123",
            "title": "New Chat",
            "description": "Desc"
        }
        
        response = client.post(
            "/api/v1/conversation/",
            json={"title": "New Chat", "description": "Desc", "project_id": "proj123"}
        )
        
        assert response.status_code == 201
        mock_repo.create.assert_called_once_with(
            title="New Chat", 
            description="Desc", 
            user_id=user_id,
            project_id="proj123"
        )

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_get_conversation_found(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.get_by_id.return_value = {
            "id": "123",
            "title": "Chat 123"
        }
        
        response = client.get("/api/v1/conversation/123")
        
        assert response.status_code == 200
        mock_repo.get_by_id.assert_called_once_with("123", user_id)

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_list_conversations_with_project(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.list_by_user.return_value = []
        
        response = client.get("/api/v1/conversation/?project_id=proj123")
        
        assert response.status_code == 200
        mock_repo.list_by_user.assert_called_once_with(user_id, "proj123")

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_delete_conversation_success(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.delete.return_value = True
        
        response = client.delete("/api/v1/conversation/123")
        
        assert response.status_code == 204
        mock_repo.delete.assert_called_once_with("123", user_id)
