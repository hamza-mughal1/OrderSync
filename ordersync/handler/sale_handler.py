from app import app
from model.sale_model import SaleModel
from model.auth_model import AuthModel

sale_model = SaleModel()
auth_model = AuthModel()

@app.route("/sales/sales", methods=["GET"])
@auth_model.token_auth()
def all_sale():
    return sale_model.all_sales()


@app.route("/sales/sales-revenue", methods=["GET"])
def sales_revenue():
    return sale_model.sales_revenue()
