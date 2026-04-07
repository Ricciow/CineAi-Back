from unittest.mock import MagicMock, patch
from bson import ObjectId
from src.repositories.project_repository import ProjectRepository

class TestProjectRepository:
    @patch("src.repositories.project_repository.projects")
    def test_create_project(self, mock_projects):
        def mock_insert(doc):
            doc["_id"] = ObjectId("60d5ecb54f1a2c001f8e4e1a")
            return MagicMock(inserted_id=doc["_id"])
            
        mock_projects.insert_one.side_effect = mock_insert

        result = ProjectRepository.create(
            name="Test Project", 
            user_id="user123", 
            description="Test Description"
        )

        assert result["name"] == "Test Project"
        assert result["user_id"] == "user123"
        assert result["description"] == "Test Description"
        assert result["id"] == "60d5ecb54f1a2c001f8e4e1a"
        mock_projects.insert_one.assert_called_once()

    @patch("src.repositories.project_repository.projects")
    def test_get_by_id_found(self, mock_projects):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_projects.find_one.return_value = {
            "_id": mock_id,
            "name": "Found Project",
            "user_id": "user123"
        }

        result = ProjectRepository.get_by_id(str(mock_id))

        assert result["name"] == "Found Project"
        assert result["id"] == str(mock_id)
        mock_projects.find_one.assert_called_once_with({"_id": mock_id})

    @patch("src.repositories.project_repository.projects")
    def test_list_by_user(self, mock_projects):
        user_id = "user123"
        mock_projects.find.return_value = [
            {"_id": ObjectId(), "name": "P1", "user_id": user_id},
            {"_id": ObjectId(), "name": "P2", "user_id": user_id}
        ]

        result = ProjectRepository.list_by_user(user_id)

        assert len(result) == 2
        assert result[0]["name"] == "P1"
        assert result[1]["name"] == "P2"
        mock_projects.find.assert_called_once_with({"user_id": user_id})

    @patch("src.repositories.project_repository.projects")
    def test_delete_success(self, mock_projects):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_projects.delete_one.return_value = MagicMock(deleted_count=1)

        result = ProjectRepository.delete(str(mock_id))

        assert result is True
        mock_projects.delete_one.assert_called_once_with({"_id": mock_id})

    @patch("src.repositories.project_repository.projects")
    def test_update_success(self, mock_projects):
        mock_id = ObjectId("60d5ecb54f1a2c001f8e4e1a")
        mock_projects.update_one.return_value = MagicMock(modified_count=1)

        update_data = {"name": "Updated Name"}
        result = ProjectRepository.update(str(mock_id), update_data)

        assert result is True
        mock_projects.update_one.assert_called_once_with(
            {"_id": mock_id},
            {"$set": update_data}
        )
