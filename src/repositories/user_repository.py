from bson import ObjectId
from src.db.session import users
from typing import Optional, Any

class UserRepository:
    @staticmethod
    def get_by_id(user_id: str) -> Optional[dict]:
        return users.find_one({"_id": ObjectId(user_id)})

    @staticmethod
    def get_by_email(email: str) -> Optional[dict]:
        return users.find_one({"email": email})

    @staticmethod
    def get_by_username(username: str) -> Optional[dict]:
        return users.find_one({"username": username})

    @staticmethod
    def create(user_data: dict) -> str:
        result = users.insert_one(user_data)
        return str(result.inserted_id)

    @staticmethod
    def update_refresh_tokens(user_id: str, refresh_token: str, push: bool = True) -> bool:
        op = "$push" if push else "$pull"
        result = users.update_one(
            {"_id": ObjectId(user_id)},
            {op: {"refreshToken": refresh_token}}
        )
        return result.modified_count > 0

user_repository = UserRepository()
