from datetime import date
from typing import Annotated, Optional
from fastapi import Query
from sqlmodel import SQLModel

class InvListModel(SQLModel):
    product_id: Optional[int] = None
    platform_id: Optional[int] = None
    min_stock_quantity: Optional[Annotated[int, Query(gt=0)]] = None
    max_stock_quantity: Optional[Annotated[int, Query(gt=0)]] = None
    offset: int = 0
    limit: Annotated[int, Query(gt=0, le=100)] = 100

class InvUpdate(SQLModel):
    product_id: int
    platform_id: int
    stock_quantity: int

class InvDelete(SQLModel):
    product_id: int
    platform_id: int

class ProductListModel(SQLModel):
    product_id: Optional[int] = None
    product_name: Optional[str] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100

class ProductInsert(SQLModel):
    product_name: str
    category_id: Optional[int]
    brand_id: Optional[int]

class ProductUpdate(SQLModel):
    product_id: int
    product_name: str
    category_id: Optional[int]
    brand_id: Optional[int]

class CategoryDataModel(SQLModel):
    category_name: str

class BrandDataModel(SQLModel):
    brand_name: str

class SalesDataModel(SQLModel):
    product_id: int
    platform_id: int
    sale_date: date
    quantity_sold: int
    sale_price: float

class SalesListModel(SQLModel):
    product_id: Optional[int] = None
    platform_id: Optional[int] = None
    sale_date: Optional[date] = None
    offset: int = 0
    limit: Annotated[int, Query(le=100)] = 100