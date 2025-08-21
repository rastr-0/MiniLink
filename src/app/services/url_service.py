from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta, timezone
from os import getenv
import logging

from src.app.models import ShortURL
from src.app.schemas import ShortenRequest, UserResponse, LinkFilters
from src.app.crud import operations
from src.app.core.utils.url import generate_short_code
from src.app.core import exceptions

logger = logging.getLogger(__name__)


async def create_short_url(data: ShortenRequest, current_user: UserResponse, d_conn: AsyncSession) -> dict:
    expiration = data.expiration_time or (datetime.now(timezone.utc) + timedelta(hours=3))

    if data.custom_alias:
        if await operations.get_link_by_code(d_conn, data.custom_alias):
            raise exceptions.CustomAliasAlreadyExists()
        short_code = data.custom_alias
    else:
        while True:
            candidate = generate_short_code(str(data.original_url))
            logger.debug(f"Looking for the candidate short code: {candidate} (user={current_user.username})")
            if not await operations.get_link_by_code(d_conn, candidate):
                short_code = candidate
                break
    try:
        link = await operations.create_short_link(
            d_conn,
            original_url=str(data.original_url),
            short_code=short_code,
            owner_id=current_user.id,
            expiration=expiration,
        )
    except SQLAlchemyError:
        logger.exception(f"Error generating short code for link: {data.original_url} by user: {current_user.username}")
        raise exceptions.ShortUrlServiceUnavailable()

    logger.info(f"Short URL successfully created for link: {link} (user={current_user.username})")

    return {
        "short_url": f"{getenv('SERVICE_URL')}{short_code}",
        "short_code": short_code,
        "created_at": link.created_at,
        "expiration_time": link.expiration_time,
        "created_by_user": current_user.id,
    }


async def get_original_url(short_code: str, db: AsyncSession) -> str:
    try:
        original_url = await operations.get_link_by_code(db, short_code)
    except SQLAlchemyError as e:
        logger.exception(f"Database error while fetching short_code={short_code}")
        raise exceptions.ShortUrlServiceUnavailable() from e

    if original_url is None:
        logger.warning(f"No URL found for short_code={short_code}")
        raise exceptions.ShortUrlNotFound(short_code)

    return original_url.long_url


async def collect_statistic(db: AsyncSession, short_code: str):
    try:
        await operations.update_short_link_clicks(db, short_code)
    except ValueError:
        logger.exception(f"Error collecting statistic short_code={short_code}")
        raise exceptions.ShortUrlNotFound(short_code)
    except SQLAlchemyError as e:
        logger.exception(f"Short_code={short_code} not found for collecting statistic")
        raise exceptions.ShortUrlNotFound(short_code) from e


async def get_statistic(short_code: str, current_user: UserResponse, db: AsyncSession) -> dict:
    try:
        original_url = await operations.get_link_by_code(db, short_code)
    except SQLAlchemyError as e:
        raise exceptions.ShortUrlNotFound() from e

    if original_url is None:
        logger.exception(f"No URL found for short_code={short_code} (user={current_user.username})")
        raise exceptions.ShortUrlNotFound(short_code)
    if original_url.user_id != current_user.id:
        logger.exception(f"User doesn't have permission to view {original_url} (user={current_user.username})")
        raise exceptions.PermessionDeniedError()

    return {"original_url": original_url.long_url, "clicks": original_url.clicks}


async def get_short_links(filters: LinkFilters, db: AsyncSession, user_id: int) -> list[ShortURL]:
    try:
        links = await operations.get_links(db, filters, user_id)
    except SQLAlchemyError as e:
        logger.exception(f"Database error while fetching links for user_id={user_id}")
        raise exceptions.ShortUrlServiceUnavailable() from e

    return list(links)
