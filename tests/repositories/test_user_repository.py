from unittest.mock import MagicMock, patch
from bson import ObjectId
from src.repositories.user_repository import UserRepository

class TestUserRepository:
    @patch("src.repositories.user_repository.users")
    def test_get_by_email(self, mock_users):
        mock_users.find_one.return_value = {"email": "test@test.com", "username": "testuser"}
        
        result = UserRepository.get_by_email("test@test.com")
        
        assert result["email"] == "test@test.com"
        mock_users.find_one.assert_called_once_with({"email": "test@test.com"})

    @patch("src.repositories.user_repository.users")
    def test_create_user(self, mock_users):
        mock_users.insert_one.return_value = MagicMock(inserted_id=ObjectId("60d5ecb54f1a2c001f8e4e1a"))
        
        user_data = {"email": "test@test.com", "senha": "hash"}
        result = UserRepository.create(user_data)
        
        assert result == "60d5ecb54f1a2c001f8e4e1a"
        mock_users.insert_one.assert_called_once_with(user_data)

    @patch("src.repositories.user_repository.users")
    def test_update_refresh_tokens_push(self, mock_users):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_users.update_one.return_value = MagicMock(modified_count=1)
        
        result = UserRepository.update_refresh_tokens(str(mock_id), "token123", push=True)
        
        assert result is True
        mock_users.update_one.assert_called_once_with(
            {"_id": mock_id},
            {"$push": {"refreshToken": "token123"}}
        )

    @patch("src.repositories.user_repository.users")
    def test_update_refresh_tokens_pull(self, mock_users):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_users.update_one.return_value = MagicMock(modified_count=1)
        
        result = UserRepository.update_refresh_tokens(str(mock_id), "token123", push=False)
        
        assert result is True
        mock_users.update_one.assert_called_once_with(
            {"_id": mock_id},
            {"$pull": {"refreshToken": "token123"}}
        )
