# types
from typing import Annotated
# fastapi
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
# pydantic models
from src.app.schemas import UserResponse, UserRequest, Token
# SQLAlchemy ORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.db.database import get_db
# SQLAlchemy models
from src.app.models.models import User
# CRUD
from src.app.crud.operations import get_existing_user, create_user
# utils
from src.app.core.utils import get_current_user, authenticate_user, create_access_token
# logs
from src.app.core.logger import requests_logger
# other
from datetime import datetime, timezone, timedelta
from os import getenv

router = APIRouter()


@router.post("/token", response_model=Token)
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    try:
        user = await authenticate_user(data.username, data.password, db)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User was not found in the system"
        )
    if not user:
        requests_logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    expiration_time = timedelta(int(getenv("EXPIRATION")))
    access_token = create_access_token(data={"sub": data.username}, expires_delta=expiration_time)

    requests_logger.info(f"User with following username: {data.username} was logged in")
    return Token(access_token=access_token, token_type="Bearer")


@router.post("/register", response_model=UserResponse)
async def register(data: UserRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    existing_user = await get_existing_user(db, data.username)
    if existing_user is not None:
        raise HTTPException(status_code=400, detail="User with the same username already registered!")
    try:
        await create_user(db, data)
        requests_logger.info(f"New user with following username: {data.username} was registered")
    except Exception as e:
        requests_logger.error(f"An error occured while register new user: {data.username}. Error: {e}")
        raise HTTPException(status_code=400, detail="New user cannot be created!")

    return UserResponse(
        username=data.username,
        created_at=datetime.now()
    )


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserResponse(
        username=current_user.username,
        created_at=datetime.now(timezone.utc)
    )
