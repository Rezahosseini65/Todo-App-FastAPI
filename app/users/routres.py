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
from app.users.security import verify_plain_against_hash, DUMMY_PASSWORD_HASH
from app.users.schemas import (
    UserLoginSchema, 
    UserRegisterSchema
)

router = APIRouter(tags=["users"], prefix="/users")


@router.post("/login/")
async def user_login(request: UserLoginSchema, db: Session = Depends(get_db)):
    """
    Authenticate a user by verifying the provided username and password.

    If the username does not exist or the password is incorrect, 
    a generic 401 error is returned to prevent username enumeration.
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

    return user_obj


@router.post("/register/")
async def user_register(request: UserRegisterSchema, db: Session = Depends(get_db)):
    """
    Register a new user account.

    Creates a new user with a hashed password after ensuring 
    the username is not already taken.
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

    return JSONResponse(
        content={"detail":"User registered successfully"},
        status_code=status.HTTP_201_CREATED
    )
