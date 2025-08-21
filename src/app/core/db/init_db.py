from src.app.models.models import Base, User, ShortURL
from src.app.core.db.database import engine


async def init_db():
    async with engine.begin() as conn:
        # await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
