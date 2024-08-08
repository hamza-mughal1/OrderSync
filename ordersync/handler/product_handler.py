from app import app
from flask import request
from model.product_model import ProductModel
from model.auth_model import AuthModel


product_model = ProductModel()
auth_model = AuthModel()


@app.route("/products/list", methods=["GET"])
@auth_model.token_auth()
def all_products():
    return product_model.all_products(
        page=request.args.get("page", default=0, type=int)
    )

@app.route("/products/add", methods=["POST"])
@auth_model.token_auth()
def add_product():
    return product_model.add_product(request.json)


@app.route("/products/delete", methods=["DELETE"])
@auth_model.token_auth()
def delete_product():
    return product_model.delete_product(request.json)


@app.route("/products/toggle", methods=["PATCH"])
@auth_model.token_auth()
def product_toggle():
    return product_model.product_toggle(
        product=request.args.get("product", default="None", type=str)
    )

@app.route("/products/get-by-category", methods=["GET"])
# @auth_model.token_auth()
def product_by_category():
    return product_model.product_by_category(request.args.get("category", default="None", type=str))

@app.route("/products/get-by-price-range", methods=["GET"])
# @auth_model.token_auth()
def products_by_price_range():
    return product_model.product_by_price_range(start = request.args.get("start", default=0, type=int),
                                             range = request.args.get("range", default=0, type=int))



