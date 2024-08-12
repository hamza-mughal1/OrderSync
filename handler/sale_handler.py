from app import app
from model.sale_model import SaleModel
from model.auth_model import AuthModel

sale_model = SaleModel()
auth_model = AuthModel()


@app.route("/sales/sales", methods=["GET"])
@auth_model.token_auth()
def all_sale():
    return sale_model.all_sales()


@app.route("/sales/revenue", methods=["GET"])
@auth_model.token_auth()
def sales_revenue():
    return sale_model.sales_revenue()


@app.route("/sales/top-products", methods=["GET"])
@auth_model.token_auth()
def top_three_products():
    return sale_model.top_three_products()


@app.route("/sales/top-selling-days", methods=["GET"])
@auth_model.token_auth()
def top_two_selling_days():
    return sale_model.top_two_selling_days()


@app.route("/sales/most-selling-hours", methods=["GET"])
@auth_model.token_auth()
def most_selling_hours():
    return sale_model.most_selling_hours()


@app.route("/sales/delta-percentage", methods=["GET"])
@auth_model.token_auth()
def delta_percentage_by_months():
    return sale_model.delta_percentage_by_months()
