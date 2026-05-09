import pytest
from src.core.security import create_access_token, create_refresh_token, verify_password, get_password_hash, decode_token
from src.core.config import settings

def test_password_hashing():
    password = "secret_password"
    hashed = get_password_hash(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrong_password", hashed) is False

def test_access_token():
    user_id = "12345"
    username = "testuser"
    email = "test@example.com"
    token = create_access_token(user_id, username, email)
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded["user_id"] == user_id
    assert decoded["username"] == username
    assert decoded["email"] == email
    assert "exp" in decoded

def test_refresh_token():
    user_id = "12345"
    token = create_refresh_token(user_id)
    assert isinstance(token, str)
    
    decoded = decode_token(token)
    assert decoded["user_id"] == user_id
    assert "exp" in decoded

def test_decode_invalid_token():
    assert decode_token("invalid_token") is None
