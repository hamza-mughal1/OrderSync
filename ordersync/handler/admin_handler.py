from app import app
from flask import request
from model.admin_model import AdminModel
from model.auth_model import AuthModel


admin_model = AdminModel()
auth_model = AuthModel()

@app.route("/add-endpoint", methods=["POST"])
def add_endpoint():
    return admin_model.add_endpoint(request.json)

