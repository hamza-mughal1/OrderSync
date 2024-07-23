from app import app
from flask import request, make_response
from model.user_model import UserModel
from model.auth_model import AuthModel


user_model = UserModel()
auth_model = AuthModel()


@app.route("/user/login", methods=["POST"])
def user_login():
    return make_response(user_model.verify_user(request.json))


@app.route("/get/all/products")
@auth_model.token_auth()
def get_all_products():
    return "all products"


@app.route("/refresh-jwt", methods=["POST"])
def refresh_jwt():
    return user_model.refresh_jwt()
