from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone
import logging

from src.app.schemas import UserResponse, UserRequest, Token
from src.app.core.db.database import get_db
from src.app.models.models import User
from src.app.core.utils import get_current_user
from src.app.core import exceptions
from src.app.services.auth_service import login_user, register_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


@router.post("/token", response_model=Token)
async def login(
        data: Annotated[OAuth2PasswordRequestForm, Depends()],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> Token:
    """
    Generate a new token for registered user.

    Args:
        data: Password request form.
        db: Active SQLAlchemy async session.
    Returns:
        Token Pydantic model.
    Raises:
        HTTPException(404) when user doesn't exist.
        HTTPException(401) when given incorrect credentials.
        HTTPException(500) when any other error occurs.
    """
    try:
        token: dict = await login_user(data, db)
    except exceptions.UserNotFoundError:
        logger.exception(f"Unable to find user (user={data.username})")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    except exceptions.InvalidPasswordError:
        logger.warning(f"Invalid credentials were given (user={data.username})")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    except exceptions.TokenCreationError:
        logger.exception(f"Failed to create token (user={data.username})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

    return Token(access_token=token['sub'], token_type=token['type'])


@router.post("/register", response_model=UserResponse)
async def register(data: UserRequest, db: Annotated[AsyncSession, Depends(get_db)]):
    """
    Register a new user.

    Args:
         data: New user request.
         db: Active SQLAlchemy async session.
    Returns:
        UserResponse Pydantic model.
    Raises:
        HTTPException(409) when user already exists.
        HTTPException(500) when any other error occurs.
    """
    try:
        user: dict = await register_user(data, db)
    except exceptions.UserAlreadyExists:
        logger.warning(f"User (user={data.username}) already exists")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )
    except exceptions.RegisterUserError as e:
        logger.exception(f"Failed to register user (user={data.username})")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        ) from e

    return UserResponse(
        id=user['id'],
        username=user['username'],
        created_at=user['created_at']
    )


@router.get("/me", response_model=UserResponse)
async def read_me(current_user: Annotated[User, Depends(get_current_user)]):
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        created_at=datetime.now(timezone.utc)
    )
