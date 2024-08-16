from app import app
from model.sale_model import SaleModel
from model.auth_model import AuthModel

# Initialize instances of the sale and authentication models
sale_model = SaleModel()
auth_model = AuthModel()


# Route to retrieve all sales data
@app.route("/sales/sales", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def all_sale():
    # Return a list of all sales
    return sale_model.all_sales()


# Route to retrieve total sales revenue
@app.route("/sales/revenue", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def sales_revenue():
    # Return the total sales revenue
    return sale_model.sales_revenue()


# Route to retrieve the top three products by sales
@app.route("/sales/top-products", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def top_three_products():
    # Return the top three products with the highest sales
    return sale_model.top_three_products()


# Route to retrieve the top two selling days
@app.route("/sales/top-selling-days", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def top_two_selling_days():
    # Return the top two days with the highest sales
    return sale_model.top_two_selling_days()


# Route to retrieve the most selling hours
@app.route("/sales/most-selling-hours", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def most_selling_hours():
    # Return the hours with the highest sales
    return sale_model.most_selling_hours()


# Route to retrieve the percentage change in sales by month
@app.route("/sales/delta-percentage", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def delta_percentage_by_months():
    # Return the percentage change in sales for each month
    return sale_model.delta_percentage_by_months()
