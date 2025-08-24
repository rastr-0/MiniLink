"""
FastAPI endpoints for URL shortening service.

Includes:
- Creating short links
- Fetching statistics
- Listing user URLs
- Deleting short URLs
"""

from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import HttpUrl
from sqlalchemy.ext.asyncio import AsyncSession
from os import getenv

from src.app.models import ShortURL
from src.app.schemas import (ShortenResponse, ShortenRequest, StatsResponse,
                             ShortResponseList, UserResponse, LinkFilters)
from src.app.core.db.database import get_db
from src.app.core.utils import get_current_user
from src.app.core import exceptions
from src.app.services.url_service import create_short_url, get_statistic, get_short_links
from src.app.crud.operations import delete_short_link
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1")


@router.post("/shorten", response_model=ShortenResponse)
async def create_shortlink(
        data: ShortenRequest,
        current_user: Annotated[UserResponse, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> ShortenResponse:
    """
    Create a new short URL for authenticated user.

    Args:
        data: Request body.
        current_user: Current user object.
        db: Active SQLAlchemy async session.
    Returns:
        Short URL pydantic model.
    Raises:
        HTTPException(409) when alias is already taken.
        HTTPException(500) when any other error occurs.
    """
    try:
        shorten_link: dict = await create_short_url(data, current_user, db)
    except exceptions.CustomAliasAlreadyExists:
        logger.warning(f"Alias {data.custom_alias} already taken (user={current_user.username})")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Alias is already taken. Try another one."
        )
    except exceptions.ShortUrlServiceUnavailable:
        logger.error(f"Failed to create short URL for user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to create a short link. Try again later."
        )

    return ShortenResponse(
        short_url=shorten_link['short_url'],
        short_code=shorten_link['short_code'],
        created_at=shorten_link['created_at'],
        expiration_time=shorten_link['expiration_time'],
        created_by_user=current_user.username
    )


@router.get("/stats/{short_code}", response_model=StatsResponse)
async def statistics(
        short_code: str,
        current_user: Annotated[UserResponse, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> StatsResponse:
    """
    Get short URL statistics.

    Args:
         short_code: Short code.
         current_user: Current user object.
         db: Active SQLAlchemy async session.
    Returns:
        Statistics pydantic model.
    Raises:
        HTTPException(404) when short URL is not present.
        HTTPException(403) when user does not have permission to access.
    """
    try:
        statistic: dict = await get_statistic(short_code, current_user, db)
    except exceptions.ShortUrlNotFound:
        logger.error(f"Short URL not found for user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )
    except exceptions.PermessionDeniedError:
        logger.error(f"Permission denied for user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied. Try logging in first"
        )

    return StatsResponse(
        original_url=statistic['original_url'],
        short_code=statistic['short_code'],
        clicks=statistic['clicks']
    )


@router.get("/my/urls", response_model=ShortResponseList)
async def get_user_links(
        current_user: Annotated[UserResponse, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)],
        filters: LinkFilters = Depends()
) -> ShortResponseList:
    """
    List user short URLs.

    Args:
         current_user: Current user object.
         db: Active SQLAlchemy async session.
         filters: Link filters.
    Returns:
        A list of Short URLs as a pydantic model.
    Raises:
        HTTPException(500) when unable to list user short URLs.
    """
    try:
        urls: list[ShortURL] = await get_short_links(filters, db, current_user.id)
    except exceptions.ShortUrlServiceUnavailable:
        logger.error(f"Internal error occured while getting links for user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Service is unavailable. Try again later"
        )

    return ShortResponseList(
        short_urls=[
            ShortenResponse(
                short_url=HttpUrl(f"{getenv('SERVICE_URL')}{url.short_code}"),
                short_code=url.short_code,
                created_at=url.created_at,
                expiration_time=url.expiration_time,
                created_by_user=current_user.username,
            )
            for url in urls
        ],
    )


@router.delete("/{short_code}", response_model=dict)
async def delete_short_url(
        short_code: str,
        current_user: Annotated[UserResponse, Depends(get_current_user)],
        db: Annotated[AsyncSession, Depends(get_db)]
) -> dict:
    """
    Delete a short URL.

    Args:
        short_code: Short URL code.
        current_user: Current user object.
        db: Active SQLAlchemy async session.
    Returns:
        Dictionary with id of deleted short URL and result status.
    Raises:
        HTTPException(404) when short URL does not exist.
    """
    deleted_id = await delete_short_link(db, current_user.id, short_code)
    if deleted_id is None:
        logger.error(f"Error deleting short URL for user={current_user.username}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Short URL not found"
        )

    return {"id": deleted_id, "result": "successfully deleted"}
