from contextlib import asynccontextmanager

from fastapi import FastAPI

from .db import create_models
from .orders.router import router as orders_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_models()
    yield

app = FastAPI(lifespan=lifespan)

app.include_router(orders_router)