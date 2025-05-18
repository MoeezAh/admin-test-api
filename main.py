from contextlib import asynccontextmanager
from datetime import datetime
from typing import Annotated, Union
from fastapi import Depends, FastAPI, HTTPException, Query
from sqlmodel import SQLModel, Session, col, create_engine, func, select

from Models.Models import *
from Models.ApiModels import BrandDataModel, CategoryDataModel, InvDeleteModel, InvListModel, InvUpdateModel, ProductInsertModel, ProductListModel, ProductUpdateModel, SalesDataModel, SalesListModel

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

# Search & filter inventory
@app.get("/inventory", tags=["Inventory"], response_model=list[Inventory], summary="Search & filter inventory.")
def get_inv(session: SessionDep,
            criteria: Annotated[InvListModel, Query()]
             ) -> list[Inventory]:
    inv = session.exec(select(Inventory)
                       .where(criteria.product_id == None or Inventory.product_id == criteria.product_id,
                              criteria.platform_id == None or Inventory.platform_id == criteria.platform_id,
                              criteria.min_stock_quantity == None or Inventory.stock_quantity >= criteria.min_stock_quantity,
                              criteria.max_stock_quantity == None or Inventory.stock_quantity <= criteria.max_stock_quantity)
                       .offset(criteria.offset)
                       .limit(criteria.limit)).all()
    return list(inv)

# Get inventory by inventory id.
@app.get("/inventory/{inventory_id}", tags=["Inventory"], response_model=Inventory, summary="Get inventory by inventory id.")
def get_inv_by_id(session: SessionDep,
             inventory_id: int) -> Inventory:
    # Get inventory by provided inventory id
    inventory = session.get(Inventory, inventory_id)

    # Riase Not Found error if inventory with provided id isn't found.
    if not inventory:
        raise HTTPException(status_code=404, detail="Inventory not found.")
    
    return inventory

# Adds or updates inventory item.
@app.post("/inventory/", tags=["Inventory"], response_model=Inventory, summary="Adds or updates inventory item.")
def update_inv(item: InvUpdateModel,
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
@app.delete("/inventory/", tags=["Inventory"], response_model=None, summary="Deletes inventory item.")
def delete_inv(item: InvDeleteModel,
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
@app.get("/product/", tags=["Product"], response_model=list[Product], summary="Lists all product.")
def get_prod(session: SessionDep,
             item: Annotated[ProductListModel, Query()]
            ) -> list[Product]:
    # Get all products using criteria, if provided.
    products = session.exec(select(Product)
                            .where(item.product_id == None or Product.product_id == item.product_id,
                                   item.product_name == None or col(Product.product_name).contains(item.product_name),
                                   item.category_id == None or Product.category_id == item.category_id,
                                   item.brand_id == None or Product.brand_id == item.brand_id)
                            .offset(item.offset)
                            .limit(item.limit)
                      ).all()
    
    return list(products)

# Get product by product id.
@app.get("/product/{product_id}", tags=["Product"], response_model=Product, summary="Get product by product id.")
def get_prod_by_id(session: SessionDep,
             product_id: int) -> Product:
    # Get product by provided product id
    product = session.get(Product, product_id)

    # Riase Not Found error if product with provided id isn't found.
    if not product:
        raise HTTPException(status_code=404, detail="Product not found.")
    
    return product

# Add a new product
@app.post("/product/", tags=["Product"], response_model=Product, summary="Adds a new product.")
def insert_prod(item: ProductInsertModel,
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
@app.put("/product/", tags=["Product"], response_model=Product, summary="Updates an existing product.")
def update_prod(item: ProductUpdateModel,
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
@app.delete("/product/", tags=["Product"], response_model=None, summary="Deletes a product by product id.")
def delete_prod(product_id: int,
               session: SessionDep
               ) -> None:
    # Deleting inventory
    product = session.get(Product, product_id)

    if product:
        session.delete(product)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="product_id is not valid.")


# List all categories
@app.get("/category/", tags=["Category"], response_model=list[Category], summary="Lists all categories.")
def get_category(session: SessionDep) -> list[Category]:
    # Get all categories using criteria, if provided.
    categories = session.exec(select(Category)).all()
    
    return list(categories)

# Get category by category id
@app.get("/category/{category_id}", tags=["Category"], response_model=Category, summary="Get category by category id.")
def get_category_by_id(session: SessionDep,
                       category_id: int
                       ) -> Category:
    # Get category by provided category id
    category = session.get(Category, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="Category id is not valid.")

    return category

# Add a new category
@app.post("/category/", tags=["Category"], response_model=Category, summary="Add a new category.")
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

# Update a category
@app.put("/category/{category_id}", tags=["Category"], response_model=Category, summary="Update a category.")
def update_category(category_id: int,
                    item: CategoryDataModel,
                    session: SessionDep
                    ) -> Category:
    # Validate category_name
    if item.category_name == None or len(item.category_name) <= 0:
        raise HTTPException(status_code=404, detail="category_name must not be empty.")

    # Getting existing category data
    category = session.get(Category, category_id)
    
    if not category:
        raise HTTPException(status_code=404, detail="category_id is not valid.")
    
    category.category_name = item.category_name

    session.commit()
    session.refresh(category)
    
    return category

# Delete a category.
@app.delete("/category/{category_id}", tags=["Category"], response_model=None, summary="Delete a category by category id.")
def delete_category(category_id: int,
               session: SessionDep
               ) -> None:
    # Deleting category
    category = session.get(Category, category_id)

    if category:
        session.delete(category)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="category_id is not valid.")


# List all brands
@app.get("/brand/", tags=["Brand"], response_model=list[Brand], summary="List all brands.")
def get_brand(session: SessionDep) -> list[Brand]:
    # Get all brands using criteria, if provided.
    brands = session.exec(select(Brand)).all()
    
    return list(brands)

# Get brand by brand id
@app.get("/brand/{brand_id}", tags=["Brand"], response_model=Brand, summary="Get brand by brand id.")
def get_brand_by_id(session: SessionDep,
                    brand_id: int
                    ) -> Brand:
    # Get brand by provided brand id
    brand = session.get(Brand, brand_id)
    
    if not brand:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")

    return brand

# Add a new brand
@app.post("/brand/", tags=["Brand"], response_model=Brand, summary="Add a new brand.")
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
@app.put("/brand/{brand_id}", tags=["Brand"], response_model=Brand, summary="Update a brand.")
def update_brand(brand_id: int,
                item: BrandDataModel,
               session: SessionDep
               ) -> Brand:
    # Validate brand_name
    if item.brand_name == None or len(item.brand_name) <= 0:
        raise HTTPException(status_code=404, detail="brand_name must not be empty.")

    # Getting existing brand data
    brand = session.get(Brand, brand_id)
    
    if not brand:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")
    
    brand.brand_name = item.brand_name

    session.commit()
    session.refresh(brand)
    
    return brand

# Delete a brand.
@app.delete("/brand/{brand_id}", tags=["Brand"], response_model=None, summary="Delete a brand by brand id.")
def delete_brand(brand_id: int,
               session: SessionDep
               ) -> None:
    # Deleting brand
    brand = session.get(Brand, brand_id)

    if brand:
        session.delete(brand)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="brand_id is not valid.")


# List all sales
@app.get("/sales/", tags=["Sale"], response_model=list[Sale], summary="List all sales.")
def get_sales(session: SessionDep,
              criteria:Annotated[SalesListModel, Query()]
              ) -> list[Sale]:
    # Get all sales using criteria, if provided.
    sales = session.exec(select(Sale)
                         .where(criteria.product_id is None or criteria.product_id == Sale.product_id,
                                criteria.platform_id is None or criteria.platform_id == Sale.platform_id,
                                criteria.sale_date is None or criteria.sale_date == Sale.sale_date)
                         .offset(criteria.offset)
                         .limit(criteria.limit)).all()
    
    return list(sales)

# Get sale by sale id
@app.get("/sale/{sale_id}", tags=["Sale"], response_model=Sale, summary="Get sale by sale id.")
def get_sale_by_id(session: SessionDep,
             sale_id: int
            ) -> Sale:
    # Get sale by provided sale id
    sale = session.get(Sale, sale_id)
    
    if not sale:
        raise HTTPException(status_code=404, detail="sale_id is not valid.")

    return sale

# Add a new sale
@app.post("/sale/", tags=["Sale"], response_model=Sale, summary="Add a new sale.")
def add_sale(item: SalesDataModel,
               session: SessionDep
               ) -> Sale:
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
    
    # Validate quantity_sold
    if item.quantity_sold <= 0:
        raise HTTPException(status_code=404, detail="quantity_sold must be greater than zero.")

    # Validate sale_price
    if item.sale_price < 0:
        raise HTTPException(status_code=404, detail="sale_price can not be a negitive number.")

    # Add sale
    sale = Sale(
        product_id= item.product_id,
        platform_id= item.platform_id,
        sale_date= item.sale_date,
        quantity_sold= item.quantity_sold,
        sale_price= item.sale_price
    )

    session.add(sale)
    session.commit()
    session.refresh(sale)
    
    return sale

# Update a sale
@app.put("/sale/{sale_id}", tags=["Sale"], response_model=Sale, summary="Update a sale.")
def update_sale(sale_id: int,
                item: SalesDataModel,
               session: SessionDep
               ) -> Sale:
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
    
    # Validate quantity_sold
    if item.quantity_sold <= 0:
        raise HTTPException(status_code=404, detail="quantity_sold must be greater than zero.")

    # Validate sale_price
    if item.sale_price < 0:
        raise HTTPException(status_code=404, detail="sale_price can not be a negitive number.")

    # Getting existing sale data
    sale = session.get(Sale, sale_id)
    
    if not sale:
        raise HTTPException(status_code=404, detail="sale_id is not valid.")
    
    sale.product_id= item.product_id
    sale.platform_id= item.platform_id
    sale.sale_date= item.sale_date
    sale.quantity_sold= item.quantity_sold
    sale.sale_price= item.sale_price

    session.commit()
    session.refresh(sale)
    
    return sale

# Delete a sale.
@app.delete("/sale/{sale_id}", tags=["Sale"], response_model=None, summary="Delete a sale by sale id.")
def delete_sale(sale_id: int,
               session: SessionDep
               ) -> None:
    # Deleting sale
    sale = session.get(Sale, sale_id)

    if sale:
        session.delete(sale)
        session.commit()
    else:
        raise HTTPException(status_code=404, detail="sale_id is not valid.")
