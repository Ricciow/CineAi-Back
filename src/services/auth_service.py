from typing import Optional, Dict, Any
from src.repositories.user_repository import user_repository
from src.core.security import (
    get_password_hash, 
    verify_password, 
    create_access_token, 
    create_refresh_token,
    decode_token
)

class AuthService:
    @staticmethod
    def register_user(email: str, password: str, username: str) -> Dict[str, Any]:
        if user_repository.get_by_email(email):
            return {"success": False, "message": "Email already exists."}
        
        if user_repository.get_by_username(username):
            return {"success": False, "message": "Username already exists."}
        
        hashed_password = get_password_hash(password)
        user_id = user_repository.create({
            "email": email,
            "senha": hashed_password,
            "username": username,
            "refreshToken": []
        })
        
        return {"success": True, "message": "User created successfully.", "user_id": user_id}

    @staticmethod
    def login(email: str, password: str) -> Dict[str, Optional[str]]:
        user = user_repository.get_by_email(email)
        if not user or not verify_password(password, user["senha"]):
            return {"token": None, "refresh_token": None}
        
        user_id = str(user["_id"])
        username = user["username"]
        
        access_token = create_access_token(user_id, username)
        refresh_token = create_refresh_token(user_id)
        
        user_repository.update_refresh_tokens(user_id, refresh_token, push=True)
        
        return {"token": access_token, "refresh_token": refresh_token}

    @staticmethod
    def logout(user_id: str, refresh_token: str) -> bool:
        return user_repository.update_refresh_tokens(user_id, refresh_token, push=False)

    @staticmethod
    def refresh_access_token(refresh_token: str) -> Optional[str]:
        payload = decode_token(refresh_token)
        if not payload:
            return None
        
        user_id = payload.get("user_id")
        user = user_repository.get_by_id(user_id)
        
        if not user or refresh_token not in user.get("refreshToken", []):
            return None
        
        return create_access_token(user_id, user["username"])

    @staticmethod
    def validate_jwt(token: str) -> Optional[str]:
        payload = decode_token(token)
        return payload.get("user_id") if payload else None

auth_service = AuthService()
