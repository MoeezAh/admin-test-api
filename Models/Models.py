from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import date


class Category(SQLModel, table=True):
    __tablename__ : str = "categories"

    category_id: Optional[int] = Field(default=None, primary_key=True)
    category_name: str

    products: List["Product"] = Relationship(back_populates="category", cascade_delete=True)


class Brand(SQLModel, table=True):
    __tablename__ : str = "brands"

    brand_id: Optional[int] = Field(default=None, primary_key=True)
    brand_name: str

    products: List["Product"] = Relationship(back_populates="brand", cascade_delete=True)


class Platform(SQLModel, table=True):
    __tablename__ : str = "platforms"

    platform_id: Optional[int] = Field(default=None, primary_key=True)
    platform_name: str

    sales: List["Sale"] = Relationship(back_populates="platform", cascade_delete=True)
    inventory: List["Inventory"] = Relationship(back_populates="platform", cascade_delete=True)


class Product(SQLModel, table=True):
    __tablename__ : str = "products"

    product_id: Optional[int] = Field(default=None, primary_key=True)
    product_name: str
    category_id: Optional[int] = Field(default=None, foreign_key="categories.category_id", ondelete="CASCADE")
    brand_id: Optional[int] = Field(default=None, foreign_key="brands.brand_id", ondelete="CASCADE")

    category: Optional[Category] = Relationship(back_populates="products")
    brand: Optional[Brand] = Relationship(back_populates="products")
    sales: List["Sale"] = Relationship(back_populates="product", cascade_delete=True)
    inventory: List["Inventory"] = Relationship(back_populates="product", cascade_delete=True)


class Sale(SQLModel, table=True):
    __tablename__ : str = "sales"

    sale_id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.product_id", ondelete="CASCADE")
    platform_id: int = Field(foreign_key="platforms.platform_id", ondelete="CASCADE")
    sale_date: date
    quantity_sold: int
    sale_price: float

    product: Optional[Product] = Relationship(back_populates="sales")
    platform: Optional[Platform] = Relationship(back_populates="sales")


class Inventory(SQLModel, table=True):
    inventory_id: Optional[int] = Field(default=None, primary_key=True)
    product_id: int = Field(foreign_key="products.product_id", ondelete="CASCADE")
    platform_id: int = Field(foreign_key="platforms.platform_id", ondelete="CASCADE")
    stock_quantity: int
    last_updated: date

    product: Optional[Product] = Relationship(back_populates="inventory")
    platform: Optional[Platform] = Relationship(back_populates="inventory")
