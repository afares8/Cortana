from datetime import timedelta
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.init_db import users_db
from app.models.user import User, UserInDB
from app.schemas.token import Token
from app.schemas.user import UserCreate

router = APIRouter()


@router.post("/login", response_model=Token)
async def login_access_token(form_data: OAuth2PasswordRequestForm = Depends()) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests.
    """
    users = users_db.get_multi(filters={"email": form_data.username})
    user = users[0] if users else None
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": create_access_token(
            subject=user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/register", response_model=User)
async def register_user(user_in: UserCreate) -> Any:
    """
    Register a new user.
    """
    existing_users = users_db.get_multi(filters={"email": user_in.email})
    if existing_users:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system",
        )
    
    user = users_db.create(
        obj_in=UserInDB(
            email=user_in.email,
            hashed_password=get_password_hash(user_in.password),
            full_name=user_in.full_name,
            is_superuser=False,
            is_active=True,
        )
    )
    
    return user
