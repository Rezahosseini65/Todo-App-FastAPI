from fastapi import APIRouter, HTTPException,status
from fastapi.responses import JSONResponse

from app.auths.jwt_auth import refresh_access_token
from app.auths.schemas import RefreshTokenRequest

router = APIRouter(tags=["auth"], prefix="/auth")

@router.post("/refresh/")
async def create_access_token(request: RefreshTokenRequest):
    """
    Generate a new access token from a valid refresh token.
    """
    new_access_token = refresh_access_token(request.refresh_token)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    return JSONResponse(
        content={
            "access_token": new_access_token,
            "token_type": "bearer"
        },
        status_code=status.HTTP_200_OK
    )

