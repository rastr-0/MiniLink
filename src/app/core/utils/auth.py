"""
Utility functions for authentication.

Includes:
- Creating an access token
- Authentication of the user
- Getting currently logged-in user

"""

from fastapi import status, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import timedelta, timezone, datetime
from typing import Annotated
from os import getenv
import logging
import jwt

from src.app.core.db.database import get_db
from src.app.crud.operations import get_existing_user
from src.app.schemas import TokenData, UserResponse
from src.app.core import exceptions
from src.app.core.utils import verify_password

logger = logging.getLogger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        # if expiration time is provided
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        # if not, then the default time is 30 minutes
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    try:
        to_encode.update({"expiration": str(expires)})
        encoded_jwt = jwt.encode(to_encode, getenv("SECRET_KEY"), getenv("ALGORITHM"))
    except jwt.InvalidKeyError as e:
        raise exceptions.TokenCreationError("Missing 'sub' in token data") from e
    except jwt.PyJWTError as e:
        raise exceptions.TokenCreationError("Failed to create JWT token") from e
    except Exception as e:
        raise exceptions.TokenCreationError("Failed to create JWT token due to unkown error") from e

    logger.info(f"Access token was successfully formed for user: {data['sub']}")

    return encoded_jwt


async def authenticate_user(
        username: str, password: str,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    user = await get_existing_user(db, username)
    if not user:
        raise SQLAlchemyError(f"Could not find user: {username} in the database")
    if verify_password(password, user.hasshed_password):
        return user
    return None


async def get_current_user(
        token: Annotated[str, Depends(oauth2_scheme)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"}
    )
    try:
        payload = jwt.decode(token, getenv("SECRET_KEY"), getenv("ALGORITHM"))
        username = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.InvalidTokenError:
        raise credentials_exception

    user = await get_existing_user(db, token_data.username)

    if user is None:
        raise credentials_exception

    logger.info(f"Information about user: {user.username} successfully retrieved")

    return UserResponse(
        id=user.id,
        username=user.username,
        created_at=datetime.now(timezone.utc)
    )
