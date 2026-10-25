from fastapi import APIRouter, Depends, HTTPException, status
from pymongo.database import Database

from ..deps import get_current_user, get_database
from ..models import CurrentUser, LoginRequest, LoginResponse
from ..security import create_token, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=LoginResponse)
def login(body: LoginRequest, db: Database = Depends(get_database)):
    user = db.users.find_one({"username": body.username})
    if user is None or not verify_password(body.password, user["password_hash"]):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid username or password")
    token = create_token(user["username"], user["role"])
    return LoginResponse(access_token=token, username=user["username"], role=user["role"])


@router.get("/me", response_model=CurrentUser)
def me(user: CurrentUser = Depends(get_current_user)):
    return user
