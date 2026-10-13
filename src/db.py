from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from .config import config

# password username
engine = create_async_engine(config.DATABSE_URL, echo = True)
Session = sessionmaker(engine, class_=AsyncSession)


class Base(DeclarativeBase):
 ...

async def get_session():
 async with Session() as s:
  yield s


async def create_models():
 async with engine.begin() as conn:
  await conn.run_sync(Base.metadata.drop_all)
  await conn.run_sync(Base.metadata.create_all)


