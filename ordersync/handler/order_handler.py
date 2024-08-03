from app import app
from flask import request
from model.order_model import OrderModel
from model.auth_model import AuthModel

order_model = OrderModel()
auth_model = AuthModel()

@app.route("/orders/place", methods=["POST"])
@auth_model.token_auth()
def place_order():
    return order_model.place_order(request.json)