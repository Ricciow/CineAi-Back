from fastapi import APIRouter, HTTPException, Depends, Response, Cookie
from fastapi.security import OAuth2PasswordBearer
from database.users import validateJWT, login as loginDatabase, register as registerDatabase, validateRefreshToken, logoff
from pydantic import BaseModel
from email_validator import validate_email
from typing import Annotated
import datetime

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """Utilizado para validar JWT e retornar o ID de usuário, para utilizar, adicione-o na função como id : str = Depends(get_current_user_id)"""
    user_id = validateJWT(token)
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user_id

class authRequest(BaseModel):
    email: str
    password: str

class registerRequest(authRequest):
    username: str

@router.post("/login")
async def login(payload: authRequest, response: Response):
    result = loginDatabase(payload.email, payload.password)
    
    if(result["token"] == None):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    
    response.set_cookie(key="refresh_token", value=result["refresh_token"], samesite="none", secure=True, max_age=int(datetime.timedelta(days=7).total_seconds()), httponly=True)

    return {"token": result["token"]}

@router.post("/login/refresh")
async def refreshToken(refresh_token: Annotated[str | None, Cookie()] = None):
    result = validateRefreshToken(refresh_token)

    if(result == None):
        raise HTTPException(status_code=401, detail="Token inválido ou expirado.")

    return {"token": result}

@router.post("/logout")
async def logout(response : Response, user_id: str = Depends(get_current_user_id), refresh_token: Annotated[str | None, Cookie()] = None):
    success = logoff(user_id, refresh_token)
    
    if(success):
        response.delete_cookie(key="refresh_token", samesite="none", secure=True)


@router.post("/register", status_code=201)
async def register(payload: registerRequest):
    try:
        validate_email(payload.email)
    except:
        raise HTTPException(status_code=400, detail="E-mail inválido.")

    result = registerDatabase(payload.email, payload.password, payload.username)
    if(result["success"]):
        return {
            "detail": result["message"]
        }
    else:
        raise HTTPException(status_code=400, detail=result["message"])