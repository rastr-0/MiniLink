from typing import Sequence
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timezone

from src.app.models.models import User, ShortURL
from src.app.schemas import UserRequest, LinkFilters
from src.app.core.utils import get_password_hash


async def get_existing_user(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    # returns exaclty one object or None, if there is more than one
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_details: UserRequest) -> User | None:
    user = User(
        username=user_details.username,
        fullname=user_details.fullname,
        hasshed_password=get_password_hash(user_details.password)
    )

    db.add(user)
    await db.commit()
    return user


async def get_link_by_code(db: AsyncSession, link_name: str) -> ShortURL | None:
    stmt = select(ShortURL).where(ShortURL.short_code == link_name)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_short_link(
        db: AsyncSession, original_url: str,
        short_code: str, owner_id: int, expiration: datetime
) -> ShortURL | None:
    link = ShortURL(
        long_url=original_url,
        short_code=short_code,
        user_id=owner_id,
        created_at=datetime.now(timezone.utc),
        expiration_time=expiration
    )
    db.add(link)
    await db.commit()

    return link


async def update_short_link_clicks(db: AsyncSession, short_code: str) -> ShortURL:
    # Operation doesn't follow an ORM-style but is atomic and guarantees the correct result
    stmt = (
        update(ShortURL)
        .where(ShortURL.short_code == short_code)
        .values(clicks=ShortURL.clicks + 1)
        .returning(ShortURL)
    )
    result = await db.execute(stmt)
    await db.commit()
    updated_url = result.scalar_one_or_none()
    if not updated_url:
        raise ValueError("Short URL not found")

    return updated_url


async def delete_short_link(db: AsyncSession, user_id: int, short_code: str) -> int | None:
    """Returns id OR None"""
    stmt = (
        delete(ShortURL)
        .where(ShortURL.short_code == short_code)
        .where(ShortURL.user_id == user_id)
        .returning(ShortURL.id)
    )
    result = await db.execute(stmt)
    await db.commit()
    return result.scalar_one_or_none()


async def get_links(db: AsyncSession, filters: LinkFilters, user_id: int) -> Sequence[ShortURL]:
    query = select(ShortURL).where(ShortURL.user_id == user_id)

    if filters.min_clicks is not None:
        query = query.where(ShortURL.clicks >= filters.min_clicks)
    if filters.max_clicks is not None:
        query = query.where(ShortURL.clicks <= filters.max_clicks)
    if filters.active is not None:
        now = datetime.now(timezone.utc)
        if filters.active:
            query = query.where(ShortURL.expiration_time < now)
        else:
            query = query.where(ShortURL.expiration_time >= now)
    if filters.created_after is not None:
        query = query.where(ShortURL.created_at < filters.created_after)
    if filters.created_before is not None:
        query = query.where(ShortURL.created_at > filters.created_before)

    query = query.offset(filters.offset).limit(filters.limit)
    result = await db.execute(query)

    return result.scalars().all()
