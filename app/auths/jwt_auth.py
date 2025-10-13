from datetime import datetime, timedelta
from typing import Dict

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db
from app.users.models import User


SECRET_KEY = settings.SECRET_KEY
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 10

security = HTTPBearer(auto_error=False)


def generate_access_token(data: Dict, expires_delta: int = ACCESS_TOKEN_EXPIRE_MINUTES)-> str:
    """
    Generate a short-lived JWT access token.
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({
        "exp":expire,
        "type":"access"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def generate_refresh_token(data: Dict, expires_delta: int=60*24*7)-> str:
    """
    Generate a long-lived JWT refresh token (default: 7 days).
    """
    to_encode = data.copy()
    expire = datetime.now() + timedelta(minutes=expires_delta)
    to_encode.update({
        "exp":expire,
        "type":"refresh"
    })
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



def refresh_access_token(refresh_token: str) -> str:
    """
    Validate the refresh token and return a new access token.
    """
    payload = verify_access_token(refresh_token, expected_type="refresh")
    if not payload:
        return None
    
    new_access_token = generate_access_token({
        "user_id":payload.get("user_id")
    })

    return new_access_token


def verify_access_token(token: str, expected_type: str = "access"):
    """
    Verify the validity and signature of a JWT token.
    Returns decoded payload or None if invalid.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != expected_type:
            return None
        
        return payload
    
    except jwt.ExpiredSignatureError:
        return None
    
    except jwt.InvalidTokenError:
        return None


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
):
    """
    Dependency to get the currently authenticated user from a valid JWT token.
    """
    # Check if credentials are not provided
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed, token not provided",
        )

    token = credentials.credentials
    payload = verify_access_token(token, expected_type="access")
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )
    
    user_id = payload.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    
    user = db.query(User).filter_by(id=user_id).first()
    if not user:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    return user 