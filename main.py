from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Session, col, create_engine, func, select

from Models.Models import *
from Models.ApiModels import BrandDataModel, CategoryDataModel, InvDelete, InvUpdate, ProductInsert, ProductUpdate

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


# List all categories
@app.get("/category/", response_model=list[Category], summary="Lists all categories.")
def get_category(session: SessionDep) -> list[Category]:
    # Get all categories using criteria, if provided.
    categories = session.exec(select(Category)).all()
    
    return list(categories)

# Get category by category id
@app.get("/category/{category_id}", response_model=Category, summary="Get category by category id.")
def get_category_by_id(session: SessionDep,
             category_id: int
            ) -> Category:
    # Get all products using criteria, if provided.
    category = session.exec(select(Category)
                       .where(category_id == Category.category_id)
                      ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="category id is not valid.")

    return category

# Add a new category
@app.post("/category/", response_model=Category, summary="Add a new category.")
def add_category(item: CategoryDataModel,
               session: SessionDep
               ) -> Category:
    # Validate category_name
    if item.category_name == None or len(item.category_name) <= 0:
        raise HTTPException(status_code=404, detail="category_name must not be empty.")

    # Add category
    category = Category(
        category_name= item.category_name
    )

    session.add(category)
    session.commit()
    session.refresh(category)
    
    return category

# Update an existing category
@app.put("/category/{category_id}", response_model=Category, summary="Update an existing category.")
def update_category(category_id: int,
                    item: CategoryDataModel,
                    session: SessionDep
                    ) -> Category:
    # Validate category_name
    if item.category_name == None or len(item.category_name) <= 0:
        raise HTTPException(status_code=404, detail="category_name must not be empty.")

    # Getting existing category data
    category = session.exec(select(Category)
                           .where(Category.category_id == category_id)
                           ).first()
    
    if not category:
        raise HTTPException(status_code=404, detail="category_id is not valid.")
    
    category.category_name = item.category_name

    session.commit()
    session.refresh(category)
    
    return category

# Delete a product.
@app.delete("/category/{category_id}", response_model=None, summary="Delete a category by category id.")
def delete_category(category_id: int,
               session: SessionDep
               ) -> None:
    # Deleting category
    category = session.exec(select(Category)
                       .where(Category.category_id == category_id)
                      ).first()

    if category:
        session.delete(category)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="category_id is not valid.")


# List all brands
@app.get("/brand/", response_model=list[Brand], summary="List all brands.")
def get_brand(session: SessionDep) -> list[Brand]:
    # Get all brands using criteria, if provided.
    brands = session.exec(select(Brand)).all()
    
    return list(brands)

# Get brand by brand id
@app.get("/brand/{brand_id}", response_model=Brand, summary="Get brand by brand id.")
def get_brand_by_id(session: SessionDep,
             brand_id: int
            ) -> Brand:
    # Get all products using criteria, if provided.
    brand = session.exec(select(Brand)
                       .where(brand_id == Brand.brand_id)
                      ).first()
    
    if not brand:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")

    return brand

# Add a new brand
@app.post("/brand/", response_model=Brand, summary="Add a new brand.")
def add_brand(item: BrandDataModel,
               session: SessionDep
               ) -> Brand:
    # Validate brand_name
    if item.brand_name == None or len(item.brand_name) <= 0:
        raise HTTPException(status_code=404, detail="brand_name must not be empty.")

    # Add brand
    brand = Brand(
        brand_name= item.brand_name
    )

    session.add(brand)
    session.commit()
    session.refresh(brand)
    
    return brand

# Update an existing brand
@app.put("/brand/{brand_id}", response_model=Brand, summary="Update a brand.")
def update_brand(brand_id: int,
                item: BrandDataModel,
               session: SessionDep
               ) -> Brand:
    # Validate brand_name
    if item.brand_name == None or len(item.brand_name) <= 0:
        raise HTTPException(status_code=404, detail="brand_name must not be empty.")

    # Getting existing brand data
    brand = session.exec(select(Brand)
                           .where(Brand.brand_id == brand_id)
                           ).first()
    
    if not brand:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")
    
    brand.brand_name = item.brand_name

    session.commit()
    session.refresh(brand)
    
    return brand

# Delete a brand.
@app.delete("/brand/{brand_id}", response_model=None, summary="Delete a brand by brand id.")
def delete_brand(brand_id: int,
               session: SessionDep
               ) -> None:
    # Deleting brand
    brand = session.exec(select(Brand)
                       .where(Brand.brand_id == brand_id)
                      ).first()

    if brand:
        session.delete(brand)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")
