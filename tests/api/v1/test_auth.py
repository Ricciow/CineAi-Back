from fastapi.testclient import TestClient
from unittest.mock import patch
from main import app

client = TestClient(app)

class TestAuthEndpoints:
    @patch("src.api.v1.endpoints.auth.auth_service")
    def test_login_success(self, mock_auth_service):
        mock_auth_service.login.return_value = {
            "token": "fake_access_token",
            "refresh_token": "fake_refresh_token"
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "test@test.com", "password": "password123"}
        )
        
        assert response.status_code == 200
        assert response.json() == {"token": "fake_access_token"}
        assert "refresh_token" in response.cookies
        assert response.cookies["refresh_token"] == "fake_refresh_token"

    @patch("src.api.v1.endpoints.auth.auth_service")
    def test_login_failure(self, mock_auth_service):
        mock_auth_service.login.return_value = {
            "token": None,
            "refresh_token": None
        }
        
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "wrong@test.com", "password": "wrongpassword"}
        )
        
        assert response.status_code == 401
        assert response.json()["detail"] == "E-mail ou senha inválidos."

    @patch("src.api.v1.endpoints.auth.auth_service")
    def test_register_success(self, mock_auth_service):
        mock_auth_service.register_user.return_value = {
            "success": True,
            "message": "User created successfully.",
            "user_id": "123"
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "new@test.com", "password": "password123", "username": "newuser"}
        )
        
        assert response.status_code == 201
        assert response.json() == {"detail": "User created successfully."}

    @patch("src.api.v1.endpoints.auth.auth_service")
    def test_register_failure(self, mock_auth_service):
        mock_auth_service.register_user.return_value = {
            "success": False,
            "message": "Email already exists."
        }
        
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "exists@test.com", "password": "password123", "username": "existinguser"}
        )
        
        assert response.status_code == 400
        assert response.json()["detail"] == "Email already exists."
