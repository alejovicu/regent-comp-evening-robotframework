"""Shared FastAPI dependencies: database and current user."""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pymongo.database import Database

from . import db as db_module
from .models import CurrentUser
from .security import decode_token

bearer = HTTPBearer(auto_error=False)


def get_database() -> Database:
    return db_module.get_db()


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> CurrentUser:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Not authenticated")
    try:
        payload = decode_token(credentials.credentials)
    except Exception:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid or expired token")
    return CurrentUser(username=payload["sub"], role=payload["role"])


def require_admin(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "admin":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Admin role required")
    return user


def require_user(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
    if user.role != "user":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Shopper role required")
    return user
