# annotations
from typing import Annotated

from sqlalchemy.exc import SQLAlchemyError
# SQLAlchemy ORM
from sqlalchemy.ext.asyncio import AsyncSession
from src.app.core.db.database import get_db
# CRUD
from src.app.crud.operations import get_existing_user
# fastapi related
from fastapi import status, HTTPException
from fastapi.params import Depends
from fastapi.security import OAuth2PasswordBearer
# security
import jwt
from jwt import InvalidTokenError
from src.app.core.utils.security import verify_password
# logging
from src.app.core.logger import internal_logger
# others
from os import getenv
from datetime import timedelta, timezone, datetime
# schemas
from src.app.schemas import TokenData, UserResponse
# exceptions
from src.app.core import exceptions
from jwt import InvalidKeyError, PyJWTError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        # if expiration time is provided
        expires = datetime.now(timezone.utc) + expires_delta
    else:
        # if not, then default time is 30 minutes
        expires = datetime.now(timezone.utc) + timedelta(minutes=30)
    try:
        to_encode.update({"expiration": str(expires)})
        encoded_jwt = jwt.encode(to_encode, getenv("SECRET_KEY"), getenv("ALGORITHM"))
        internal_logger.info(f"Access token was successfully formed for user: {data['sub']}")
    except InvalidKeyError as e:
        raise exceptions.TokenCreationError("Missing 'sub' in token data") from e
    except PyJWTError as e:
        raise exceptions.TokenCreationError("Failed to create JWT token") from e
    except Exception as e:
        raise exceptions.TokenCreationError("Failed to create JWT token due to unkown error") from e

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
    except InvalidTokenError:
        raise credentials_exception

    user = await get_existing_user(db, token_data.username)

    if user is None:
        raise credentials_exception

    internal_logger.info(f"Information about user: {user.username} successfully retrieved")

    return UserResponse(
        username=user.username,
        created_at=datetime.now(timezone.utc)
    )
