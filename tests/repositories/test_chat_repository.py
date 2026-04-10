from unittest.mock import MagicMock, patch
from bson import ObjectId
from src.repositories.chat_repository import ChatRepository

class TestChatRepository:
    @patch("src.repositories.chat_repository.chats")
    def test_create_chat(self, mock_chats):
        def mock_insert(doc):
            doc["_id"] = ObjectId("60d5ecb54f1a2c001f8e4e1a")
            return MagicMock(inserted_id=doc["_id"])
            
        mock_chats.insert_one.side_effect = mock_insert

        result = ChatRepository.create(
            title="Test Title", 
            description="Test Description", 
            user_id="user123", 
            project_id="proj456"
        )

        assert result["title"] == "Test Title"
        assert result["user_id"] == "user123"
        assert result["project_id"] == "proj456"
        assert result["id"] == "60d5ecb54f1a2c001f8e4e1a"
        mock_chats.insert_one.assert_called_once()

    @patch("src.repositories.chat_repository.chats")
    def test_get_by_id_found(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        user_id = "user123"
        mock_chats.find_one.return_value = {
            "_id": mock_id,
            "title": "Found Title",
            "user_id": user_id,
            "messages": []
        }

        result = ChatRepository.get_by_id(str(mock_id), user_id)

        assert result["title"] == "Found Title"
        assert result["id"] == str(mock_id)
        mock_chats.find_one.assert_called_once_with({"_id": mock_id, "user_id": user_id})

    @patch("src.repositories.chat_repository.chats")
    def test_list_by_user_with_project(self, mock_chats):
        user_id = "user123"
        project_id = "proj456"
        mock_chats.find.return_value = [
            {"_id": ObjectId(), "title": "C1", "user_id": user_id, "project_id": project_id}
        ]

        result = ChatRepository.list_by_user(user_id, project_id)

        assert len(result) == 1
        mock_chats.find.assert_called_once_with(
            {"user_id": user_id, "project_id": project_id},
            {"title": 1, "description": 1, "project_id": 1}
        )

    @patch("src.repositories.chat_repository.chats")
    def test_delete_success(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        user_id = "user123"
        mock_chats.delete_one.return_value = MagicMock(deleted_count=1)

        result = ChatRepository.delete(str(mock_id), user_id)

        assert result is True
        mock_chats.delete_one.assert_called_once_with({"_id": mock_id, "user_id": user_id})

    @patch("src.repositories.chat_repository.chats")
    def test_get_history(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        user_id = "user123"
        messages = [{"role": "user", "content": "hello"}]
        mock_chats.find_one.return_value = {"messages": messages}

        result = ChatRepository.get_history(str(mock_id), user_id)

        assert result == messages
        mock_chats.find_one.assert_called_once_with({"_id": mock_id, "user_id": user_id}, {"messages": 1})

    @patch("src.repositories.chat_repository.chats")
    def test_add_message(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        user_id = "user123"
        message = {"role": "assistant", "content": "hi"}
        mock_chats.update_one.return_value = MagicMock(modified_count=1)

        result = ChatRepository.add_message(str(mock_id), message, user_id)

        assert result is True
        mock_chats.update_one.assert_called_once_with(
            {"_id": mock_id, "user_id": user_id}, 
            {"$push": {"messages": message}}
        )
