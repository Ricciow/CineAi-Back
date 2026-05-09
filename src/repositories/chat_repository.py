from bson import ObjectId
from src.db.session import chats
from typing import List, Optional, Any

class ChatRepository:
    @staticmethod
    def create(title: str, description: str, user_id: str, project_id: Optional[str] = None) -> dict:
        chat_document = {
            "title": title, 
            "description": description, 
            "user_id": user_id,
            "project_id": project_id,
            "messages": []
        }
        chats.insert_one(chat_document)
        chat_document["id"] = str(chat_document.pop("_id"))
        return chat_document

    @staticmethod
    def delete(chat_id: str, user_id: Optional[str] = None) -> bool:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        result = chats.delete_one(query)
        return result.deleted_count > 0

    @staticmethod
    def get_history(chat_id: str, user_id: Optional[str] = None) -> Optional[List[dict]]:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        doc = chats.find_one(query, {"messages": 1})
        return doc.get("messages") if doc else None

    @staticmethod
    def get_by_id(chat_id: str, user_id: Optional[str] = None) -> Optional[dict]:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        doc = chats.find_one(query)
        if doc:
            doc["id"] = str(doc.pop("_id"))
        return doc

    @staticmethod
    def list_by_user(user_id: str, project_id: Optional[str] = None) -> List[dict]:
        if project_id:
            query = {"project_id": project_id}
        else:
            query = {"user_id": user_id, "project_id": None}
            
        cursor = chats.find(query, {"title": 1, "description": 1, "project_id": 1})
        results = []
        for doc in cursor:
            doc["id"] = str(doc.pop("_id"))
            results.append(doc)
        return results

    @staticmethod
    def add_message(chat_id: str, message: dict, user_id: Optional[str] = None) -> bool:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        result = chats.update_one(
            query, 
            {"$push": {"messages": message}}
        )
        return result.modified_count > 0

    @staticmethod
    def update_title(chat_id: str, title: str, user_id: Optional[str] = None) -> bool:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        result = chats.update_one(
            query, 
            {"$set": {"title": title}}
        )
        return result.modified_count > 0

    @staticmethod
    def update_description(chat_id: str, description: str, user_id: Optional[str] = None) -> bool:
        query = {"_id": ObjectId(chat_id)}
        if user_id:
            query["user_id"] = user_id
        result = chats.update_one(
            query, 
            {"$set": {"description": description}}
        )
        return result.modified_count > 0

chat_repository = ChatRepository()
