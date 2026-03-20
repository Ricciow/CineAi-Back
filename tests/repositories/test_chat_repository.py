from unittest.mock import MagicMock, patch
from bson import ObjectId
from src.repositories.chat_repository import ChatRepository

class TestChatRepository:
    @patch("src.repositories.chat_repository.chats")
    def test_create_chat(self, mock_chats):
        # Mock insert_one to simulate MongoDB behavior
        def mock_insert(doc):
            doc["_id"] = ObjectId("60d5ecb54f1a2c001f8e4e1a")
            return MagicMock(inserted_id=doc["_id"])
            
        mock_chats.insert_one.side_effect = mock_insert

        result = ChatRepository.create("Test Title", "Test Description")

        assert result["title"] == "Test Title"
        assert result["description"] == "Test Description"
        assert result["id"] == "60d5ecb54f1a2c001f8e4e1a"
        mock_chats.insert_one.assert_called_once()

    @patch("src.repositories.chat_repository.chats")
    def test_get_by_id_found(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_chats.find_one.return_value = {
            "_id": mock_id,
            "title": "Found Title",
            "messages": []
        }

        result = ChatRepository.get_by_id(str(mock_id))

        assert result["title"] == "Found Title"
        assert result["id"] == str(mock_id)
        mock_chats.find_one.assert_called_once_with({"_id": mock_id})

    @patch("src.repositories.chat_repository.chats")
    def test_get_by_id_not_found(self, mock_chats):
        mock_chats.find_one.return_value = None

        result = ChatRepository.get_by_id(str(ObjectId()))

        assert result is None

    @patch("src.repositories.chat_repository.chats")
    def test_add_message_success(self, mock_chats):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_chats.update_one.return_value = MagicMock(modified_count=1)

        message = {"role": "user", "content": "Hello"}
        result = ChatRepository.add_message(str(mock_id), message)

        assert result is True
        mock_chats.update_one.assert_called_once_with(
            {"_id": mock_id},
            {"$push": {"messages": message}}
        )
