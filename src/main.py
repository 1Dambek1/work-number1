from fastapi import FastAPI
from src.orders.router import router as orders_router

app = FastAPI()

app.include_router(orders_router)
