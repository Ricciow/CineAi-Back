from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database.users import validateJWT, login as loginDatabase, register as registerDatabase
from pydantic import BaseModel
from email_validator import validate_email

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

async def get_current_user_id(token: str = Depends(oauth2_scheme)):
    """Utilizado para validar JWT e retornar o ID de usuário, para utilizar, adicione-o na função como id : str = Depends(get_current_user_id)"""
    payload = validateJWT(token)
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id = payload.get("user_id")
    return user_id

class authRequest(BaseModel):
    email: str
    password: str

class registerRequest(authRequest):
    username: str

@router.post("/login")
async def login(payload: authRequest):
    token = loginDatabase(payload.email, payload.password)
    
    if(token == None):
        raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
    
    return {"token": token}

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