from app import app
from flask import request
from model.order_model import OrderModel
from model.auth_model import AuthModel

# Initialize instances of the order and authentication models
order_model = OrderModel()
auth_model = AuthModel()


# Route to handle placing an order
@app.route("/orders/place", methods=["POST"])
@auth_model.token_auth()  # Requires token authentication
def place_order():
    # Place an order using data from the request
    return order_model.place_order(request.json)
