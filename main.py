from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Session, col, create_engine, func, select

from Models.Models import *
from Models.ApiModels import InvDelete, InvUpdate, ProductInsert, ProductUpdate

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = { "check_same_thread": False }
engine = create_engine(sqlite_url, connect_args = connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDep = Annotated[Session, Depends(get_session)]

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_db_and_tables()
    yield
    pass

app = FastAPI(lifespan=lifespan)

# API Endpoints

@app.get("/inventory")
def read_inv(session: SessionDep,
             offset: int = 0,
             limit: Annotated[int, Query(le=100)] = 100
             ) -> list[Inventory]:
    inv = session.exec(select(Inventory).offset(offset).limit(limit)).all()
    return list(inv)

# Adds or updates inventory item.
@app.post("/inventory/", response_model=Inventory, summary="Adds or updates inventory item.")
def update_inv(item: InvUpdate,
               session: SessionDep
               ) -> Inventory:
    # Validate product_id
    prod_count = session.scalar(select(func.count(col(Product.product_id)))
                           .where(Product.product_id == item.product_id))
    if not prod_count == 1:
        raise HTTPException(status_code=404, detail="product_id is not valid.")
    
    # Validate platform_id
    platform_count = session.scalar(select(func.count(col(Platform.platform_id)))
                           .where(Platform.platform_id == item.platform_id))
    if not platform_count == 1:
        raise HTTPException(status_code=404, detail="platform_id is not valid.")
    
    # Validate stock_quantity
    if item.stock_quantity < 0:
        raise HTTPException(status_code=404, detail="stock_quantity must be zero or more.")

    # Updating inventory
    inv = session.exec(select(Inventory)
                       .where(Inventory.platform_id == item.platform_id,
                              Inventory.product_id == item.product_id)
                      ).first()
    if not inv:
       # raise HTTPException(status_code=404, detail="Inventory data is not valid.")
       inv = Inventory(
           product_id= item.product_id,
           platform_id = item.platform_id,
           stock_quantity= item.stock_quantity,
           last_updated = datetime.now()
       )
       session.add(inv)
    else:
        inv.stock_quantity = item.stock_quantity
        inv.last_updated = datetime.now()

    session.commit()
    session.refresh(inv)
    
    return inv

# Deletes inventory item.
@app.delete("/inventory/", response_model=None, summary="Deletes inventory item.")
def delete_inv(item: InvDelete,
               session: SessionDep
               ) -> None:
    # Validate product_id
    prod_count = session.scalar(select(func.count(col(Product.product_id)))
                           .where(Product.product_id == item.product_id))
    if not prod_count == 1:
        raise HTTPException(status_code=404, detail="product_id is not valid.")
    
    # Validate platform_id
    platform_count = session.scalar(select(func.count(col(Platform.platform_id)))
                           .where(Platform.platform_id == item.platform_id))
    if not platform_count == 1:
        raise HTTPException(status_code=404, detail="platform_id is not valid.")

    # Deleting inventory
    inv = session.exec(select(Inventory)
                       .where(Inventory.platform_id == item.platform_id,
                              Inventory.product_id == item.product_id)
                      ).first()
    if inv:
        session.delete(inv)
        session.commit()

# List all products
@app.get("/product/", response_model=list[Product], summary="Lists all product.")
def get_prod(session: SessionDep,
             category_id: Optional[int] = None,
             brand_id: Optional[int] = None
            ) -> list[Product]:
    # Get all products using criteria, if provided.
    products = session.exec(select(Product)
                       .where((category_id == None or Product.category_id == category_id)
                              and (brand_id == None or Product.brand_id == brand_id))
                      ).all()
    
    return list(products)

# Add a new product
@app.post("/product/", response_model=Product, summary="Adds a new product.")
def insert_prod(item: ProductInsert,
               session: SessionDep
               ) -> Product:
    # Validate category_id
    category_count = session.scalar(select(func.count(col(Category.category_id)))
                           .where(Category.category_id == item.category_id))
    if not category_count == 1:
        raise HTTPException(status_code=404, detail="category_id is not valid.")
    
    # Validate brand_id
    brand_count = session.scalar(select(func.count(col(Brand.brand_id)))
                           .where(Brand.brand_id == item.brand_id))
    if not brand_count == 1:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")
    
    # Validate product_name
    if item.product_name == None or len(item.product_name) <= 0:
        raise HTTPException(status_code=404, detail="product_name must not be empty.")

    # Add product
    product = Product(
        product_name= item.product_name,
        category_id= item.category_id,
        brand_id= item.brand_id
    )

    session.add(product)
    session.commit()
    session.refresh(product)
    
    return product

# Updates an existing product
@app.put("/product/", response_model=Product, summary="Updates an existing product.")
def update_prod(item: ProductUpdate,
               session: SessionDep
               ) -> Product:
    # Validate category_id
    category_count = session.scalar(select(func.count(col(Category.category_id)))
                           .where(Category.category_id == item.category_id))
    if not category_count == 1:
        raise HTTPException(status_code=404, detail="category_id is not valid.")
    
    # Validate brand_id
    brand_count = session.scalar(select(func.count(col(Brand.brand_id)))
                           .where(Brand.brand_id == item.brand_id))
    if not brand_count == 1:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")
    
    # Validate product_name
    if item.product_name == None or len(item.product_name) <= 0:
        raise HTTPException(status_code=404, detail="product_name must not be empty.")

    # Getting existing product data
    product = session.exec(select(Product)
                           .where(Product.product_id == item.product_id)
                           ).one()
    
    product.product_name = item.product_name
    product.category_id = item.category_id
    product.brand_id = item.brand_id

    session.commit()
    session.refresh(product)
    
    return product

# Deletes a product.
@app.delete("/product/", response_model=None, summary="Deletes a product by product id.")
def delete_prod(product_id: int,
               session: SessionDep
               ) -> None:
    # Deleting inventory
    product = session.exec(select(Product)
                       .where(Product.product_id == product_id)
                      ).first()

    if product:
        session.delete(product)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="product_id is not valid.")