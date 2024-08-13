from app import app
from flask import request, make_response
from model.user_model import UserModel
from model.auth_model import AuthModel


user_model = UserModel()
auth_model = AuthModel()


@app.route("/users/login", methods=["POST"])
def user_login():
    return make_response(user_model.verify_user(request.json))


@app.route("/users/refresh", methods=["POST"])
def refresh_jwt():
    return user_model.refresh_jwt()


@app.route("/users/logout", methods=["POST"])
def logout():
    return user_model.logout()


@app.route("/users/logout-all", methods=["POST"])
def logout_all():
    return user_model.logout_all()


@app.route("/users/users", methods=["POST"])
@auth_model.token_auth()
def create_user():
    return user_model.create_user(request.json)


@app.route("/users/users", methods=["DELETE"])
@auth_model.token_auth()
def delete_user():
    return user_model.delete_user(request.json)
