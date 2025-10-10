import jwt
from datetime import datetime, timedelta
from typing import Dict

from app.core.config import settings

SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

def generate_access_token(data: Dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES)-> str:
    """
    Generate a short-lived JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_refresh_token(data: Dict, expires_delta: int=60*24*7)-> str:
    """
    Validate the refresh token and return a new access token.
    """
    return generate_access_token(data=data, expires_delta=expires_delta)


def refresh_access_token(refresh_token: str) -> str:
    """
    Generate a long-lived JWT refresh token (default: 7 days).
    """
    payload = verify_access_token(refresh_token)
    if not payload:
        return None
    
    new_access_token = generate_access_token({
        "user_id":payload.get("user_id")
    })

    return new_access_token


def verify_access_token(token: str):
    """
    Verify the validity and signature of a JWT token.
    Returns decoded payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    
    except jwt.InvalidTokenError:
        return None


