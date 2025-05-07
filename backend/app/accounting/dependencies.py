from typing import Optional, List, Dict, Any
from fastapi import Depends, HTTPException, status
from app.core.security import oauth2_scheme
from app.db.init_db import users_db
from jose import jwt, JWTError
from app.core.config import settings
from app.accounting.services import user_can_access_company


async def get_current_user(token: str = Depends(oauth2_scheme)):
    """Get the current user from the token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    users = users_db.get_multi(filters={"id": int(user_id)})
    user = users[0] if users else None
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user",
        )
    
    return user


def company_read_permission(company_id: int):
    """Dependency for checking read permission for a company."""
    async def check_permission(current_user = Depends(get_current_user)):
        if settings.BYPASS_ACCOUNTING_PERMISSIONS:
            return current_user
            
        if not user_can_access_company(current_user.id, company_id, "read"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to access this company",
            )
        return current_user
    return check_permission


def company_write_permission(company_id: int):
    """Dependency for checking write permission for a company."""
    async def check_permission(current_user = Depends(get_current_user)):
        if settings.BYPASS_ACCOUNTING_PERMISSIONS:
            return current_user
            
        if not user_can_access_company(current_user.id, company_id, "write"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions to modify this company",
            )
        return current_user
    return check_permission


def admin_only():
    """Dependency for admin-only endpoints."""
    async def check_admin(current_user = Depends(get_current_user)):
        if settings.BYPASS_ACCOUNTING_PERMISSIONS:
            return current_user
            
        if not (current_user.is_superuser or getattr(current_user, "role", None) == "admin"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Admin access required",
            )
        return current_user
    return check_admin
