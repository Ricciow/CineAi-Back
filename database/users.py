from database.database import users
from argon2 import PasswordHasher
import jwt
import datetime
from dotenv import load_dotenv
from bson import ObjectId
import os


# Estrutura de um usuário:
# {
#   "_id": "user_id_abc",
#   "email": "usuario@email.com",
#   "username": "username",
#   "senha": "hash_da_senha",
#   "refreshToken": ["refresh_token"]
# }

load_dotenv()
SECRET_KEY = os.environ.get("SECRET_KEY")

ph = PasswordHasher()

def register(email, senha, username):
    exists = users.find_one({"$or": [{"email": email}, {"username": username}]})
    if(exists):
        if(exists["email"] == email):
            return {
                "message": "Email already exists.",
                "success": False
            }
        else:
            return {
                "message": "Username already exists.",
                "success": False
            }
    
    senha = ph.hash(senha)

    user_document = {
        "email": email, 
        "senha": senha,
        "username": username
    }

    users.insert_one(user_document)
    user_document["_id"] = str(user_document["_id"])

    return {
        "message": "User created successfully.",
        "success": True
    }

def login(email, senha):
    """Valida login e retorna um JWT"""
    user_document = users.find_one({"email": email})
    if not user_document:
        return {
            "token": None
        }

    if not validateUser(user_document, senha):
        return {
            "token": None
        }

    refresh_token = jwt.encode({
        "user_id": str(user_document["_id"]), 
        "exp": datetime.datetime.now() + datetime.timedelta(days=7)
        }, 
        key=SECRET_KEY,
        algorithm="HS256"
    )

    users.update_one({"email": email}, {
        "$push": {
            "refreshToken": refresh_token
        }
    })

    token = jwt.encode({
        "user_id": str(user_document["_id"]), 
        "username": user_document["username"],
        "exp": datetime.datetime.now() + datetime.timedelta(minutes=15)
        }, 
        key=SECRET_KEY,
        algorithm="HS256"
    )

    return {
        "token": token,
        "refresh_token": refresh_token
    }

def logoff(user_id, refresh_token):
    users.update_one({"_id": ObjectId(user_id)}, {
        "$pull": {
            "refreshToken": refresh_token
        }
    })

def validateRefreshToken(refresh_token):
    """Valida token de refresh e retorna um jwt de usuário novo se válido"""
    try:
        payload = jwt.decode(refresh_token, key=SECRET_KEY, algorithms=["HS256"])

        user_document = users.find_one({"_id": ObjectId(payload["user_id"])})

        if(not refresh_token in user_document["refreshToken"]):
            return None

        if not user_document:
            return None

        token = jwt.encode({
            "user_id": str(user_document["_id"]), 
            "username": user_document["username"],
            "exp": datetime.datetime.now() + datetime.timedelta(minutes=15)
            }, 
            key=SECRET_KEY,
            algorithm="HS256"
        )

        return token

    except:
        return None

def validateJWT(token):
    """Valida JWT e retorna user_id se válido"""
    try:
        payload = jwt.decode(token, key=SECRET_KEY, algorithms=["HS256"])
        return payload["user_id"]
    except:
        return None

def validateUser(user_document, senha):
    try:
        ph.verify(user_document["senha"], senha)
        return True
    except:
        return False