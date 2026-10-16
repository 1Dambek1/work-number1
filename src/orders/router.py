from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import get_session
from src.models import User, Products, UserProducts

router = APIRouter(prefix="/orders", tags=["orders"])

class UserCreate(BaseModel):
    username: str
    password: str

class UserOut(BaseModel):
    id: int
    username: str
    model_config = {"from_attributes": True}

class ProductCreate(BaseModel):
    name: str
    price: float

class ProductOut(BaseModel):
    id: int
    name: str
    price: float
    model_config = {"from_attributes": True}

class UserProductOut(BaseModel):
    user_id: int
    product_id: int
    quantity: int
    model_config = {"from_attributes": True}

class TopProductOut(BaseModel):
    id: int
    name: str
    price: float
    total_quantity: int

@router.post("/users", response_model=UserOut)
async def create_user(data: UserCreate, session: AsyncSession = Depends(get_session)):
    user = User(username=data.username, password=data.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user

@router.post("/products", response_model=ProductOut)
async def create_product(data: ProductCreate, session: AsyncSession = Depends(get_session)):
    product = Products(name=data.name, price=data.price)
    session.add(product)
    await session.commit()
    await session.refresh(product)
    return product

@router.get("/products", response_model=list[ProductOut])
async def get_products(
        name: str,
        min_price: float,
        max_price: float,
        session: AsyncSession = Depends(get_session),
):
    query = select(Products)
    if name:
        query = query.where(Products.name.like(f"%{name}%"))
    if min_price is not None:
        query = query.where(Products.price >= min_price)
    if max_price is not None:
        query = query.where(Products.price <= max_price)
    result = await session.scalars(query)
    return list(result)

@router.post("/users/{user_id}/products/{product_id}", response_model=UserProductOut)
async def add_product_to_user(
    user_id: int,
    product_id: int,
    session: AsyncSession = Depends(get_session),
):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")
    product = await session.get(Products, product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Продукт не найден")

    item = await session.scalar(
        select(UserProducts).where(
            UserProducts.user_id == user_id,
            UserProducts.product_id == product_id,
        )
    )
    if item is None:
        item = UserProducts(user_id=user_id, product_id=product_id, quantity=1)
        session.add(item)
    else:
        item.quantity += 1

    await session.commit()
    await session.refresh(item)
    return item

@router.get("/users/{user_id}/cart/total")
async def get_cart_total(user_id: int, session: AsyncSession = Depends(get_session)):
    user = await session.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    total = await session.scalar(
        select(func.sum(Products.price * UserProducts.quantity))
        .join(UserProducts, UserProducts.product_id == Products.id)
        .where(UserProducts.user_id == user_id)
    )
    return {"user_id": user_id, "total": total or 0}

@router.get("/products/top", response_model=list[TopProductOut])
async def get_top_products(session: AsyncSession = Depends(get_session)):
    total = func.sum(UserProducts.quantity).label("total_quantity")
    result = await session.execute(
        select(Products.id, Products.name, Products.price, total)
        .join(UserProducts, UserProducts.product_id == Products.id)
        .group_by(Products.id)
        .order_by(total.desc())
        .limit(3)
    )
    return result.all()