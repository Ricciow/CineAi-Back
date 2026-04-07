from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app
from src.api.deps import get_current_user_id

client = TestClient(app)

# Mock dependency
def override_get_current_user_id():
    return "60d5ecb54f1a2c001f8e4e1a"

app.dependency_overrides[get_current_user_id] = override_get_current_user_id

class TestProjectEndpoints:
    @patch("src.api.v1.endpoints.project.project_repository")
    def test_create_project(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.create.return_value = {
            "id": "123",
            "name": "New Project",
            "description": "Desc",
            "user_id": user_id
        }
        
        response = client.post(
            "/api/v1/project/",
            json={"name": "New Project", "description": "Desc"}
        )
        
        assert response.status_code == 201
        assert response.json()["id"] == "123"
        mock_repo.create.assert_called_once_with(
            name="New Project", 
            user_id=user_id, 
            description="Desc"
        )

    @patch("src.api.v1.endpoints.project.project_repository")
    def test_get_project_found(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.get_by_id.return_value = {
            "id": "123",
            "name": "Project 123",
            "user_id": user_id
        }
        
        response = client.get("/api/v1/project/123")
        
        assert response.status_code == 200
        assert response.json()["name"] == "Project 123"

    @patch("src.api.v1.endpoints.project.project_repository")
    def test_get_project_unauthorized(self, mock_repo):
        # Different user
        mock_repo.get_by_id.return_value = {
            "id": "123",
            "name": "Project 123",
            "user_id": "another_user"
        }
        
        response = client.get("/api/v1/project/123")
        
        assert response.status_code == 404
        assert response.json()["detail"] == "Projeto não encontrado."

    @patch("src.api.v1.endpoints.project.project_repository")
    def test_list_projects(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.list_by_user.return_value = [
            {"id": "1", "name": "P1", "user_id": user_id},
            {"id": "2", "name": "P2", "user_id": user_id}
        ]
        
        response = client.get("/api/v1/project/")
        
        assert response.status_code == 200
        assert len(response.json()) == 2
        mock_repo.list_by_user.assert_called_once_with(user_id)

    @patch("src.api.v1.endpoints.project.project_repository")
    def test_delete_project_success(self, mock_repo):
        user_id = "60d5ecb54f1a2c001f8e4e1a"
        mock_repo.get_by_id.return_value = {"id": "123", "user_id": user_id}
        mock_repo.delete.return_value = True
        
        response = client.delete("/api/v1/project/123")
        
        assert response.status_code == 204
