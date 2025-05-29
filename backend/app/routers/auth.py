from datetime import timedelta
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm

from app.core.config import settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.db.init_db import users_db
from app.models.user import User, UserInDB
from app.schemas.token import Token
from app.schemas.user import UserCreate
from app.services.email import send_email
from app.modules.admin.roles.services import assign_role

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
async def register_user(
    user_in: UserCreate,
    background_tasks: BackgroundTasks
) -> Any:
    """
    Register a new user.
    
    This endpoint:
    1. Creates a new user account
    2. Assigns default roles to the user
    3. Sends an activation email
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
    
    try:
        assign_role({
            "user_id": user.id,
            "department_id": 1,  # Legal department
            "role_id": 1,        # Basic User role
        })
    except Exception as e:
        print(f"Error assigning default role: {e}")
    
    async def send_activation_email(user_email: str, user_name: str):
        subject = "Welcome to Cortana - Account Activation"
        body = f"""
        Dear {user_name},
        
        Your account has been successfully created in the Cortana system.
        
        Your account is now active and you can log in using your email and password.
        
        If you did not request this account, please contact the administrator.
        
        Regards,
        The Cortana Team
        """
        await send_email(email_to=user_email, subject=subject, body=body)
    
    background_tasks.add_task(
        send_activation_email,
        user_email=user.email,
        user_name=user.full_name
    )
    
    return user
