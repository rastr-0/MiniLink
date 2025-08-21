from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm
# logging
from src.app.core.logger import requests_logger
# utils
from src.app.core.utils import authenticate_user, create_access_token
# CRUD
from src.app.crud.operations import get_existing_user, create_user
# other
from datetime import datetime, timezone, timedelta
from os import getenv

from src.app.schemas import UserRequest
from src.app.core import exceptions


async def login_user(data: OAuth2PasswordRequestForm, db_conn: AsyncSession) -> dict:
    try:
        user = await authenticate_user(data.username, data.password, db_conn)
    except SQLAlchemyError as e:
        requests_logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.UserNotFoundError("User not found") from e
    except Exception as e:
        requests_logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.UserNotFoundError("Error loging in due to unkown error") from e

    if not user:
        requests_logger.error(f"Unsuccessful attempt to log in by: {data.username}")
        raise exceptions.InvalidPasswordError("Invalid credentials")

    expiration_time = timedelta(int(getenv("EXPIRATION")))
    access_token = create_access_token(data={"sub": data.username}, expires_delta=expiration_time)

    requests_logger.info(f"User with following username: {data.username} was logged in")

    return {"sub": access_token, "type": "Bearer"}


async def register_user(data: UserRequest, db_conn: AsyncSession) -> dict:
    existing_user = await get_existing_user(db_conn, data.username)
    if existing_user is not None:
        raise exceptions.UserAlreadyExists("User with the same username is already registered")
    try:
        user = await create_user(db_conn, data)
    except SQLAlchemyError as e:
        requests_logger.error(f"An error occured while register new user: {data.username}. Error: {e}")
        raise exceptions.RegisterUserError("New user cannot be created") from e

    requests_logger.info(f"New user with following username: {user.username} was registered")

    return {
        "id": user.id,
        "username": user.username,
        "created_at": datetime.now(timezone.utc)
    }
