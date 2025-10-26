from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from database.users import validateJWT, login as loginDatabase, register as registerDatabase

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

@router.post("/login")
async def login(email: str, senha: str):
    token = loginDatabase(email, senha)
    return {"token": token}

@router.post("/register", status_code=201)
async def register(email: str, senha: str):
    if(registerDatabase(email, senha)):
        return {"message": "User created successfully."}
    else:
        raise HTTPException(status_code=400, detail="Erro ao criar usuário.")
    
