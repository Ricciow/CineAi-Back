from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app
from src.api.deps import get_current_user_id, get_current_user

client = TestClient(app)

OWNER_ID = "60d5ecb54f1a2c001f8e4e1a"
ADMIN_ID = "60d5ecb54f1a2c001f8e4e1b"
MEMBER_ID = "60d5ecb54f1a2c001f8e4e1c"

def override_get_current_user_id():
    return OWNER_ID

def override_get_current_user():
    return {"id": OWNER_ID, "email": "owner@example.com"}

app.dependency_overrides[get_current_user_id] = override_get_current_user_id
app.dependency_overrides[get_current_user] = override_get_current_user

class TestProjectAccess:
    @patch("src.api.v1.endpoints.project.project_repository")
    @patch("src.api.v1.endpoints.project.user_repository")
    def test_add_member_as_owner(self, mock_user_repo, mock_project_repo):
        mock_project_repo.get_by_id.return_value = {
            "id": "project123",
            "user_id": OWNER_ID,
            "members": []
        }
        mock_user_repo.get_by_email.return_value = {
            "_id": MagicMock(return_value=MEMBER_ID),
            "email": "member@example.com"
        }
        mock_user_repo.get_by_email.return_value["_id"] = MEMBER_ID

        response = client.post(
            "/api/v1/project/project123/members",
            json={"email": "member@example.com", "role": "member"}
        )

        assert response.status_code == 201
        assert response.json()["message"] == "Membro adicionado com sucesso"
        mock_project_repo.add_member.assert_called_once()

    @patch("src.api.v1.endpoints.project.project_repository")
    @patch("src.api.v1.endpoints.project.user_repository")
    def test_add_admin_as_owner(self, mock_user_repo, mock_project_repo):
        mock_project_repo.get_by_id.return_value = {
            "id": "project123",
            "user_id": OWNER_ID,
            "members": []
        }
        mock_user_repo.get_by_email.return_value = {
            "_id": ADMIN_ID,
            "email": "admin@example.com"
        }

        response = client.post(
            "/api/v1/project/project123/members",
            json={"email": "admin@example.com", "role": "admin"}
        )

        assert response.status_code == 201
        mock_project_repo.add_member.assert_called_once()
        assert mock_project_repo.add_member.call_args[0][1]["role"] == "admin"

    @patch("src.api.v1.endpoints.project.project_repository")
    def test_add_member_as_admin_failure(self, mock_project_repo):
        def override_admin_user_id(): return ADMIN_ID
        app.dependency_overrides[get_current_user_id] = override_admin_user_id
        
        mock_project_repo.get_by_id.return_value = {
            "id": "project123",
            "user_id": OWNER_ID,
            "members": [{"user_id": ADMIN_ID, "email": "admin@example.com", "role": "admin"}]
        }

        response = client.post(
            "/api/v1/project/project123/members",
            json={"email": "member@example.com", "role": "admin"} # Trying to add another admin
        )

        assert response.status_code == 403
        assert response.json()["detail"] == "Apenas o dono pode adicionar administradores"
        
        app.dependency_overrides[get_current_user_id] = override_get_current_user_id

    @patch("src.api.v1.endpoints.project.project_repository")
    @patch("src.api.v1.endpoints.project.user_repository")
    def test_transfer_ownership(self, mock_user_repo, mock_project_repo):
        mock_project_repo.get_by_id.return_value = {
            "id": "project123",
            "user_id": OWNER_ID,
            "members": [{"user_id": ADMIN_ID, "email": "admin@example.com", "role": "admin"}]
        }
        mock_user_repo.get_by_email.return_value = {
            "_id": ADMIN_ID,
            "email": "admin@example.com"
        }

        response = client.post(
            "/api/v1/project/project123/transfer-ownership",
            json={"new_owner_email": "admin@example.com"}
        )

        assert response.status_code == 200
        mock_project_repo.update.assert_called_with("project123", {"user_id": ADMIN_ID})
        mock_project_repo.remove_member.assert_called_with("project123", "admin@example.com")
        mock_project_repo.add_member.assert_called_once() # Adding old owner back as admin
