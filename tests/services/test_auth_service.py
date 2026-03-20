from unittest.mock import patch
from src.services.auth_service import AuthService

class TestAuthService:
    @patch("src.services.auth_service.user_repository")
    @patch("src.services.auth_service.get_password_hash")
    def test_register_user_success(self, mock_get_password_hash, mock_user_repo):
        # Mocking data
        mock_user_repo.get_by_email.return_value = None
        mock_user_repo.get_by_username.return_value = None
        mock_get_password_hash.return_value = "hashed_password"
        mock_user_repo.create.return_value = "user_id_123"

        result = AuthService.register_user("test@test.com", "password123", "testuser")

        assert result["success"] is True
        assert result["user_id"] == "user_id_123"
        mock_user_repo.create.assert_called_once()

    @patch("src.services.auth_service.user_repository")
    def test_register_user_email_exists(self, mock_user_repo):
        # Mocking data
        mock_user_repo.get_by_email.return_value = {"email": "test@test.com"}

        result = AuthService.register_user("test@test.com", "password123", "testuser")

        assert result["success"] is False
        assert result["message"] == "Email already exists."
        mock_user_repo.create.assert_not_called()

    @patch("src.services.auth_service.user_repository")
    @patch("src.services.auth_service.verify_password")
    @patch("src.services.auth_service.create_access_token")
    @patch("src.services.auth_service.create_refresh_token")
    def test_login_success(self, mock_create_refresh, mock_create_access, mock_verify_password, mock_user_repo):
        # Mocking data
        mock_user_repo.get_by_email.return_value = {
            "_id": "60d5ecb54f1a2c001f8e4e1a",
            "email": "test@test.com",
            "senha": "hashed_password",
            "username": "testuser"
        }
        mock_verify_password.return_value = True
        mock_create_access.return_value = "access_token_123"
        mock_create_refresh.return_value = "refresh_token_123"

        result = AuthService.login("test@test.com", "password123")

        assert result["token"] == "access_token_123"
        assert result["refresh_token"] == "refresh_token_123"
        mock_user_repo.update_refresh_tokens.assert_called_once()

    @patch("src.services.auth_service.user_repository")
    @patch("src.services.auth_service.verify_password")
    def test_login_invalid_password(self, mock_verify_password, mock_user_repo):
        # Mocking data
        mock_user_repo.get_by_email.return_value = {
            "email": "test@test.com",
            "senha": "hashed_password"
        }
        mock_verify_password.return_value = False

        result = AuthService.login("test@test.com", "wrong_password")

        assert result["token"] is None
        assert result["refresh_token"] is None
        mock_user_repo.update_refresh_tokens.assert_not_called()
