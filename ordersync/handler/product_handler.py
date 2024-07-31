from app import app
from flask import request
from model.product_model import ProductModel
from model.auth_model import AuthModel


product_model = ProductModel()
auth_model = AuthModel()


@app.route("/products/products", methods=["GET"])
# @auth_model.token_auth()
def all_products():
    return product_model.all_products(page=request.args.get('page', default=0, type=int))

@app.route("/products/orders", methods=["POST"])
@auth_model.token_auth()
def place_order():
    return product_model.place_order(request.json)

@app.route("/products/products", methods=["POST"])
@auth_model.token_auth()
def add_product():
    return product_model.add_product(request.json)

@app.route("/products/products", methods=["DELETE"])
@auth_model.token_auth()
def delete_product():
    return product_model.delete_product(request.json)
