from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)
from fastapi.responses import JSONResponse

from sqlalchemy.orm import Session

from app.core.database import get_db
from app.users.models import User
from app.auths.jwt_auth import generate_access_token, generate_refresh_token
from app.users.security import verify_plain_against_hash, DUMMY_PASSWORD_HASH
from app.users.schemas import (
    UserLoginSchema, 
    UserRegisterSchema
)

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/login/")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    """
    Authenticate an existing user and issue JWT tokens.

    - Verifies username and password.
    - Returns both `access_token` and `refresh_token` if authentication succeeds.
    - Returns a generic 401 error for invalid credentials to prevent user enumeration.
    """
    user_obj = db.query(User).filter_by(username=request.username).first()

    if not user_obj:
        verify_plain_against_hash(request.password, DUMMY_PASSWORD_HASH)
        raise HTTPException(
            detail={"message": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    if not verify_plain_against_hash(request.password, user_obj.password):
        raise HTTPException(
            detail={"message": "Invalid username or password"},
            status_code=status.HTTP_401_UNAUTHORIZED
        )

    access_token = generate_access_token({"user_id":user_obj.id})
    refresh_token = generate_refresh_token({"user_id":user_obj.id})

    return JSONResponse(
        content={
            "access_token":access_token,
            "refresh_token":refresh_token, 
            "token_type":"bearer"
        },status_code=status.HTTP_200_OK
    )


@router.post("/register/")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user account and issue JWT tokens.

    - Creates a new user with a hashed password.
    - Ensures the username is unique.
    - Returns both `access_token` and `refresh_token` after successful registration.
    """
    if db.query(User).filter_by(username=request.username.lower()).first():
        raise HTTPException(
            detail="username alredy exists",
            status_code=status.HTTP_400_BAD_REQUEST
        )
    
    user_obj = User(username=request.username.lower())
    user_obj.set_password(request.password)
    db.add(user_obj)
    db.commit()
    db.refresh(user_obj)

    access_token = generate_access_token({"user_id":user_obj.id})
    refresh_token = generate_refresh_token({"user_id":user_obj.id})

    return JSONResponse(
        content={
            "access_token":access_token,
            "refresh_token":refresh_token, 
            "token_type":"bearer"
        },status_code=status.HTTP_201_CREATED
    )