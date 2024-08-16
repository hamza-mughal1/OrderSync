from app import app
from flask import request
from model.category_model import CategoryModel
from model.auth_model import AuthModel

# Initialize instances of the category and authentication models
category_model = CategoryModel()
auth_model = AuthModel()


# Route to handle toggling a category's status
@app.route("/categories/category-toggle", methods=["PATCH"])
@auth_model.token_auth()  # Requires token authentication
def category_toggle():
    # Toggle the category status using the category name from the request arguments
    return category_model.category_toggle(
        category=request.args.get("category", default="None", type=str)
    )
