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
        mock_repo.create.return_value = {
            "id": "123",
            "title": "New Chat",
            "description": "Desc"
        }
        
        response = client.post(
            "/api/v1/conversation/",
            json={"title": "New Chat", "description": "Desc"}
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == "123"
        mock_repo.create.assert_called_once_with("New Chat", "Desc")

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_get_conversation_found(self, mock_repo):
        mock_repo.get_by_id.return_value = {
            "id": "123",
            "title": "Chat 123"
        }
        
        response = client.get("/api/v1/conversation/123")
        
        assert response.status_code == 200
        assert response.json()["title"] == "Chat 123"

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_get_conversation_not_found(self, mock_repo):
        mock_repo.get_by_id.return_value = None
        
        response = client.get("/api/v1/conversation/999")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Conversa não encontrada."

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_list_conversations(self, mock_repo):
        mock_repo.list_all_descriptions.return_value = [
            {"id": "1", "title": "Chat 1"},
            {"id": "2", "title": "Chat 2"}
        ]
        
        response = client.get("/api/v1/conversation/")
        
        assert response.status_code == 200
        assert len(response.json()) == 2

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_delete_conversation_success(self, mock_repo):
        mock_repo.delete.return_value = True
        
        response = client.delete("/api/v1/conversation/123")
        
        assert response.status_code == 204

    @patch("src.api.v1.endpoints.conversation.chat_repository")
    def test_update_conversation_title(self, mock_repo):
        mock_repo.update_title.return_value = True
        
        response = client.patch(
            "/api/v1/conversation/123",
            json={"title": "Updated Title"}
        )
        
        assert response.status_code == 200
        assert response.json()["detail"] == "Título atualizado com sucesso"
