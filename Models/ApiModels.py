from typing import Optional
from sqlmodel import SQLModel

class InvUpdate(SQLModel):
    product_id: int
    platform_id: int
    stock_quantity: int

class InvDelete(SQLModel):
    product_id: int
    platform_id: int

class ProductInsert(SQLModel):
    product_name: str
    category_id: Optional[int]
    brand_id: Optional[int]

class ProductUpdate(SQLModel):
    product_id: int
    product_name: str
    category_id: Optional[int]
    brand_id: Optional[int]

class CategoryInsert(SQLModel):
    category_name: str

class CategoryUpdate(SQLModel):
    category_id: int
    category_name: str