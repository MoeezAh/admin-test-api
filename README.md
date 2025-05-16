## Packages

This application requires following top level packages.

- [FastAPI](https://fastapi.tiangolo.com/) - `fastapi[standar]`
- [SQLModel](https://sqlmodel.tiangolo.com/) - `sqlmodel`

## End Points

### GET /inventory

### POST /inventory/{product_id}

Updates quantity of a product for a specific platform.

### DELETE /inventory/{product_id}

### GET /product

Lists all available products

### POST /product

Creates new product.

### PUT /product/{product_id}

Updates existing product.

### DELETE /product/{product_id}

Deletes existing product, along with all its related data from sales and inventory.

### GET /category

### POST /category

### PUT /category/{category_id}

### DELETE /category/{category_id}

### GET /brand

### POST /brand

### PUT /brand/{brand_id}

### DELETE /brand/{brand_id}

### GET /sales

### POST /sales

### PUT /sales/{sales_id}

### DELETE /sales/{sales_id}
