from app import app
from flask import request
from model.category_model import CategoryModel
from model.auth_model import AuthModel


category_model = CategoryModel()
auth_model = AuthModel()


@app.route("/categories/category-toggle", methods=["PATCH"])
@auth_model.token_auth()
def category_toggle():
    return category_model.category_toggle(
        category=request.args.get("category", default="None", type=str)
    )

