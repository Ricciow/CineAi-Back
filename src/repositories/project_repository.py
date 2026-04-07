from bson import ObjectId
from src.db.session import projects
from typing import List, Optional

class ProjectRepository:
    @staticmethod
    def create(name: str, user_id: str, description: Optional[str] = None) -> dict:
        project_document = {
            "name": name, 
            "description": description, 
            "user_id": user_id
        }
        projects.insert_one(project_document)
        project_document["id"] = str(project_document.pop("_id"))
        return project_document

    @staticmethod
    def get_by_id(project_id: str) -> Optional[dict]:
        doc = projects.find_one({"_id": ObjectId(project_id)})
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    @staticmethod
    def list_by_user(user_id: str) -> List[dict]:
        cursor = projects.find({"user_id": user_id})
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    @staticmethod
    def delete(project_id: str) -> bool:
        result = projects.delete_one({"_id": ObjectId(project_id)})
        return result.deleted_count > 0

    @staticmethod
    def update(project_id: str, data: dict) -> bool:
        result = projects.update_one(
            {"_id": ObjectId(project_id)}, 
            {"$set": data}
        )
        return result.modified_count > 0

project_repository = ProjectRepository()
