from app import app
from flask import request
from model.sale_model import SaleModel
from model.auth_model import AuthModel


sale_model = SaleModel()
auth_model = AuthModel()

@app.route("/all-sale")
def all_sale():
    return sale_model.all_sales()