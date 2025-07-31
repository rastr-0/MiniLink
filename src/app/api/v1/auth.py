# types
from typing import Annotated
# fastapi
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
# pydantic models
from src.app.schemas import UserResponse, UserRequest, Token
# SQLAlchemy ORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.db.database import get_db
# SQLAlchemy models
from src.app.models.models import User
# utils
from src.app.core.utils.auth import get_current_user
# other
from datetime import datetime, timezone
# exceptions
from src.app.core import exceptions
# buiseness logic
from src.app.services.auth_service import login_user, register_user

router = APIRouter(prefix="/api/v1")


@router.post("/token", response_model=Token)
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    try:
        token: dict = await login_user(data, db)
    except exceptions.UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except exceptions.InvalidPasswordError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    except exceptions.TokenCreationError:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    return Token(access_token=token['sub'], token_type=token['type'])


@router.post("/register", response_model=UserResponse)
async def register(data: UserRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    try:
        user: dict = await register_user(data, db)
    except exceptions.UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except (exceptions.RegisterUserError, Exception):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    return UserResponse(
        username=user['username'],
        created_at=user['created_at']
    )


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserResponse(
        username=current_user.username,
        created_at=datetime.now(timezone.utc)
    )
