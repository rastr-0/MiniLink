from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone, timedelta
import logging
from os import getenv

from src.app.core.utils import authenticate_user, create_access_token
from src.app.crud.operations import get_existing_user, create_user
from src.app.schemas import UserRequest
from src.app.core import exceptions

logger = logging.getLogger(__name__)


async def login_user(data: OAuth2PasswordRequestForm, db_conn: AsyncSession) -> dict:
    try:
        user = await authenticate_user(data.username, data.password, db_conn)
    except SQLAlchemyError as e:
        logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.UserNotFoundError("User not found") from e
    except Exception as e:
        logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.UserNotFoundError("Error loging in due to unkown error") from e

    if not user:
        logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.InvalidPasswordError("Invalid credentials")

    expiration_time = timedelta(int(getenv("EXPIRATION")))
    access_token = create_access_token(data={"sub": data.username}, expires_delta=expiration_time)

    logger.info(f"User with following username: {data.username} was logged in")

    return {"sub": access_token, "type": "Bearer"}


async def register_user(data: UserRequest, db_conn: AsyncSession) -> dict:
    existing_user = await get_existing_user(db_conn, data.username)
    if existing_user is not None:
        raise exceptions.UserAlreadyExists("User with the same username is already registered")
    try:
        user = await create_user(db_conn, data)
    except SQLAlchemyError as e:
        logger.error(f"An error occured while register new user: {data.username}. Error: {e}")
        raise exceptions.RegisterUserError("New user cannot be created") from e

    logger.info(f"New user with following username: {user.username} was registered")

    return {
        "id": user.id,
        "username": user.username,
        "created_at": datetime.now(timezone.utc)
    }
