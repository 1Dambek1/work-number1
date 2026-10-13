from .db import Base
from sqlalchemy.orm import mapped_column, Mapped,relationship
from sqlalchemy import ForeignKey


class User(Base):
 __tablename__ = "users"
 id:Mapped[int] = mapped_column(primary_key=True)
 username:Mapped[str]
 password:Mapped[str]
 products:Mapped[list["Products"]] = relationship()


class UserProducts(Base):
 __tablename__ = "users_products"
 id:Mapped[int] = mapped_column(primary_key=True)
 quantity:Mapped[int]
 user_id:Mapped[int] = mapped_column(ForeignKey("users.id"))
 product_id:Mapped[int] = mapped_column(ForeignKey("products.id"))


class Products(Base):
 __tablename__ = "products"
 id:Mapped[int] = mapped_column(primary_key=True)
 username:Mapped[str]
 price:Mapped[float]

