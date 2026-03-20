import pytest
from fastapi import HTTPException
from unittest.mock import patch
from src.api.deps import get_current_user_id

class TestDeps:
    @patch("src.api.deps.auth_service")
    def test_get_current_user_id_success(self, mock_auth_service):
        mock_auth_service.validate_jwt.return_value = "user_123"
        
        user_id = get_current_user_id("valid_token")
        
        assert user_id == "user_123"
        mock_auth_service.validate_jwt.assert_called_once_with("valid_token")

    @patch("src.api.deps.auth_service")
    def test_get_current_user_id_failure(self, mock_auth_service):
        mock_auth_service.validate_jwt.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_current_user_id("invalid_token")
            
        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "Token inválido ou expirado"
