from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
# schemas + models
from src.app.models.models import User
from src.app.schemas import UserRequest
# utils
from src.app.core.security import get_password_hash


async def get_existing_user(db: AsyncSession, username: str) -> User | None:
    stmt = select(User).where(User.username == username)
    result = await db.execute(stmt)
    # returns exaclty one object or None, if there is more than one
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, user_details: UserRequest):
    db.add(
        User(
            username=user_details.username,
            fullname=user_details.fullname,
            hasshed_password=get_password_hash(user_details.password)
        )
    )
    await db.commit()
