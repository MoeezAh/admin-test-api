## Packages

This application requires following top level packages.

- [FastAPI](https://fastapi.tiangolo.com/) - `fastapi[standar]`
- [SQLModel](https://sqlmodel.tiangolo.com/) - `sqlmodel`

## End Points

### GET /inventory

### POST /inventory/`{product_id}`

Updates quantity of a product for a specific platform.

### DELETE /inventory/`{product_id}`

### GET /product

Lists all available products

### GET /product/`{product_id}`

Gets a product by its id.

### POST /product

Creates new product.

### PUT /product/`{product_id}`

Updates existing product.

### DELETE /product/`{product_id}`

Deletes existing product, along with all its related data from sales and inventory.

### GET /category

Lists all categories.

### GET /category/`{category_id}`

Get a category data by its id.

### POST /category

Creates a new category.

### PUT /category/`{category_id}`

Updates existing category.

### DELETE /category/`{category_id}`

Deletes a category along with its all related data.

### GET /brand

List all brands.

### GET /brand/`{brand_id}`

Get a brand data by its id.

### POST /brand

Create a new brand

### PUT /brand/`{brand_id}`

Updates existing brand

### DELETE /brand/`{brand_id}`

Deletes a brand along with its all realated data.

### GET /sales

List all sales.

### GET /sales/`{sale_id}`

Get sale data by sale id.

### POST /sales

Adds a new sale.

### PUT /sales/`{sales_id}`

Updates an existing sale data.

### DELETE /sales/`{sales_id}`

Deletes a sale by sale id.
