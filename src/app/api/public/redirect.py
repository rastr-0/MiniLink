from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from typing import Annotated
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.core.db.database import get_db
from src.app.core import exceptions
from src.app.services.url_service import get_original_url, collect_statistic
from src.app.core.logger import requests_logger

public_router = APIRouter()


@public_router.get("/{short_code}", response_class=RedirectResponse, status_code=status.HTTP_307_TEMPORARY_REDIRECT)
async def redirect(
        short_code: str,
        db: Annotated[AsyncSession, Depends(get_db)]
):
    """
    Redirect to the original URL.

    Args:
        short_code: The short code to redirect.
        db: Active SQLAlchemy async session.
    Returns:
        A redirect response(307).
    Raises:
        HTTPException(404) when URL is not found or is invalid.
        HTTPException(503) when other error occurs.
    """
    try:
        long_url: str = await get_original_url(short_code, db)
    except exceptions.ShortUrlNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to find redirection for given URL. Try adding URL first"
        )
    except exceptions.InvalidShortUrl:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Unable to redirect with the given URL. Try checking the format"
        )
    except exceptions.ShortUrlServiceUnavailable:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="URL shortening service currently unavailable. Try again later"
        )

    await collect_statistic(db, short_code)

    return long_url
