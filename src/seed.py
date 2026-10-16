import asyncio
from src.db import Base, Session, engine
from src.models import User, Products, UserProducts


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    users = [
        User(username="anna", password="123"),
        User(username="boris", password="123"),
        User(username="vera", password="123"),
        User(username="gleb", password="123"),
        User(username="dasha", password="123"),
    ]
    products = [
        Products(name="Яблоко", price=50),
        Products(name="Банан", price=80),
        Products(name="Яблочный сок", price=120),
        Products(name="Молоко", price=95),
        Products(name="Хлеб", price=45),
        Products(name="Сыр", price=450),
        Products(name="Кофе", price=600),
        Products(name="Чай", price=250),
    ]

    async with Session() as session:
        session.add_all(users + products)
        await session.commit()

        purchases = [
            (1, 1, 3), (1, 2, 2), (1, 5, 1),
            (2, 1, 2), (2, 4, 4), (2, 7, 1),
            (3, 2, 2), (3, 3, 2), (3, 4, 1), (3, 8, 1),
            (4, 1, 1), (4, 5, 2), (4, 6, 1),
            (5, 4, 2), (5, 3, 1),
        ]
        session.add_all(
            UserProducts(user_id=u, product_id=p, quantity=q)
            for u, p, q in purchases
        )
        await session.commit()

if __name__ == "__main__":
    asyncio.run(seed())