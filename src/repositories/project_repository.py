from bson import ObjectId
from src.db.session import projects
from typing import List, Optional

class ProjectRepository:
    @staticmethod
    def create(name: str, user_id: str, description: Optional[str] = None) -> dict:
        project_document = {
            "name": name, 
            "description": description, 
            "user_id": user_id,
            "members": []
        }
        projects.insert_one(project_document)
        project_document["id"] = str(project_document.pop("_id"))
        return project_document

    @staticmethod
    def get_by_id(project_id: str) -> Optional[dict]:
        doc = projects.find_one({"_id": ObjectId(project_id)})
        if doc:
            doc["id"] = str(doc.pop("_id"))
            if "members" not in doc:
                doc["members"] = []
        return doc

    @staticmethod
    def list_by_user(user_id: str) -> List[dict]:
        # Search for projects where the user is owner OR a member
        cursor = projects.find({
            "$or": [
                {"user_id": user_id},
                {"members.user_id": user_id}
            ]
        })
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            if "members" not in doc:
                doc["members"] = []
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
        return result.matched_count > 0

    @staticmethod
    def add_member(project_id: str, member_data: dict) -> bool:
        result = projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$push": {"members": member_data}}
        )
        return result.modified_count > 0

    @staticmethod
    def update_member(project_id: str, email: str, update_data: dict) -> bool:
        # Construct the $set dictionary for the specific member in the list
        set_op = {}
        for key, value in update_data.items():
            if key == "permissions":
                for p_key, p_value in value.items():
                    set_op[f"members.$.permissions.{p_key}"] = p_value
            else:
                set_op[f"members.$.{key}"] = value

        result = projects.update_one(
            {"_id": ObjectId(project_id), "members.email": email},
            {"$set": set_op}
        )
        return result.modified_count > 0

    @staticmethod
    def remove_member(project_id: str, email: str) -> bool:
        result = projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"email": email}}}
        )
        return result.modified_count > 0

    @staticmethod
    def transfer_ownership(project_id: str, old_owner_id: str, new_owner_id: str, new_owner_email: str) -> bool:
        # 1. Update the project user_id to the new owner
        # 2. Add the old owner as an admin in the members list
        # We'll use a transaction if possible, but for simplicity in this Mongo setup:
        
        # Check if new owner is already in members, if so remove them from members list
        projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$pull": {"members": {"user_id": new_owner_id}}}
        )

        # Update owner
        projects.update_one(
            {"_id": ObjectId(project_id)},
            {"$set": {"user_id": new_owner_id}}
        )
        
        # Add old owner as admin
        # We need the old owner's email. For now, let's assume the service handles this logic
        # and we just take the data.
        return True

project_repository = ProjectRepository()
