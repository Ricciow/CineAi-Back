from pydantic import BaseModel, EmailStr

class AuthRequest(BaseModel):
    email: EmailStr
    password: str

class RegisterRequest(AuthRequest):
    username: str

class Token(BaseModel):
    token: str

class LoginResponse(Token):
    refresh_token: str
