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

