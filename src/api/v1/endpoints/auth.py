from datetime import timedelta
from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Response, Cookie, status
from src.schemas.auth import AuthRequest, RegisterRequest, Token
from src.services.auth_service import auth_service
from src.api.deps import get_current_user_id
from src.core.config import settings

router = APIRouter()

@router.post("/login", response_model=Token)
async def login(payload: AuthRequest, response: Response):
    result = auth_service.login(payload.email, payload.password)
    
    if result["token"] is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="E-mail ou senha inválidos."
        )
    
    response.set_cookie(
        key="refresh_token", 
        value=result["refresh_token"], 
        samesite="none", 
        secure=True, 
        max_age=int(timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS).total_seconds()), 
        httponly=True
    )

    return {"token": result["token"]}

@router.post("/login/refresh", response_model=Token)
async def refresh_token(refresh_token: Annotated[Optional[str], Cookie()] = None):
    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Refresh token ausente."
        )
    
    new_token = auth_service.refresh_access_token(refresh_token)
    if new_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Token inválido ou expirado."
        )

    return {"token": new_token}

@router.post("/logout")
async def logout(
    response: Response, 
    user_id: str = Depends(get_current_user_id), 
    refresh_token: Annotated[Optional[str], Cookie()] = None
):
    if refresh_token:
        auth_service.logout(user_id, refresh_token)
    
    response.delete_cookie(key="refresh_token", samesite="none", secure=True)
    return {"detail": "Logout bem-sucedido"}

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def register(payload: RegisterRequest):
    if not settings.ALLOW_REGISTRATION:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="O cadastro de novos usuários está temporariamente desativado."
        )
    result = auth_service.register_user(payload.email, payload.password, payload.username)
    if result["success"]:
        return {"detail": result["message"]}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=result["message"]
        )
