from contextlib import asynccontextmanager
from fastapi import FastAPI
from src.app.api.v1.convert import router as convert_router
from src.app.api.v1.auth import router as auth_router
from src.app.api.public.redirect import public_router
from src.app.core.db.init_db import init_db
from src.app.core.logger import setup_logging, LOGGING_CONFIG
from dotenv import load_dotenv

setup_logging(log_config=LOGGING_CONFIG)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    load_dotenv()
    await init_db()
    yield


app = FastAPI(lifespan=lifespan, debug=True)

app.include_router(router=convert_router)
app.include_router(router=auth_router)
app.include_router(router=public_router)
