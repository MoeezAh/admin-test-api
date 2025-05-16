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

### GET /product/{product_id}

Gets a product by its id.

### POST /product

Creates new product.

### PUT /product/{product_id}

Updates existing product.

### DELETE /product/`{product_id}`

Deletes existing product, along with all its related data from sales and inventory.

`product_id` should be a valid product id.

### GET /category

Lists all categories.

### POST /category

Creates a new category.

### PUT /category/`{category_id}`

Updates existing category.

### DELETE /category/`{category_id}`

Deletes a category along with its all related data.

### GET /brand

### POST /brand

### PUT /brand/{brand_id}

### DELETE /brand/{brand_id}

### GET /sales

### POST /sales

### PUT /sales/{sales_id}

### DELETE /sales/{sales_id}
