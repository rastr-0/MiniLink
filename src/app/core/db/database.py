from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from src.app.core.settings import settings

engine = create_async_engine(settings.get_url(), echo=True)
SessionLocal = async_sessionmaker(engine, expire_on_commit=False)


async def get_db():
    async with SessionLocal() as session:
        yield session
    # await session.close()
