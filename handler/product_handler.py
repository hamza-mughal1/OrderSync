from app import app
from flask import request
from model.product_model import ProductModel
from model.auth_model import AuthModel

# Initialize instances of the product and authentication models
product_model = ProductModel()
auth_model = AuthModel()


# Route to retrieve a list of all products with optional pagination
@app.route("/products/list", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def all_products():
    # Return a list of all products, with optional pagination based on the 'page' query parameter
    return product_model.all_products(
        page=request.args.get("page", default=0, type=int)
    )


# Route to add a new product
@app.route("/products/add", methods=["POST"])
@auth_model.token_auth()  # Requires token authentication
def add_product():
    # Add a new product using data from the request
    return product_model.add_product(request.json)


# Route to delete a product
@app.route("/products/delete", methods=["DELETE"])
@auth_model.token_auth()  # Requires token authentication
def delete_product():
    # Delete a product using data from the request
    return product_model.delete_product(request.json)


# Route to toggle the status of a product
@app.route("/products/toggle", methods=["PATCH"])
@auth_model.token_auth()  # Requires token authentication
def product_toggle():
    # Toggle the product status using the product name from the request arguments
    return product_model.product_toggle(
        product=request.args.get("product", default="None", type=str)
    )


# Route to retrieve products by category
@app.route("/products/get-by-category", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def product_by_category():
    # Return products filtered by category using the category from the request arguments
    return product_model.product_by_category(
        request.args.get("category", default="None", type=str)
    )


# Route to retrieve products by price range
@app.route("/products/get-by-price-range", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def products_by_price_range():
    # Return products within a specified price range using the start and range parameters from the request arguments
    return product_model.product_by_price_range(
        start=request.args.get("start", default=0, type=int),
        range=request.args.get("range", default=0, type=int),
    )


# Route to upload an image for a product
@app.route("/products/upload-image/<product_name>", methods=["PUT"])
@auth_model.token_auth()  # Requires token authentication
def upload_product_image(product_name):
    # Upload an image for the specified product using the product name and files from the request
    return product_model.upload_product_image(product_name, request.files)


# Route to retrieve an image of a product
@app.route("/products/image/<product_name>", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def get_product_image(product_name):
    # Return the image of the specified product using the product name
    return product_model.get_product_image(product_name)
