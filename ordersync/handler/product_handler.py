from app import app
from flask import request, make_response
from model.product_model import ProductModel
from model.auth_model import AuthModel


product_model = ProductModel()
auth_model = AuthModel()


@app.route("/all-products/<int:page>")
@auth_model.token_auth(endpoint="/all-products")
def all_products(page):
    return product_model.all_products(page=page)

@app.route("/place-order", methods=["POST"])
def place_order():
    return product_model.place_order(request.json)
