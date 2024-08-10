from app import app
from flask import request
from model.admin_model import AdminModel
from model.auth_model import AuthModel

admin_model = AdminModel()
auth_model = AuthModel()

@app.route("/admin/endpoints", methods=["POST"])
def create_endpoint():
    return admin_model.create_endpoint(request.json)

@app.route("/admin/endpoints", methods=["PUT"])
def update_endpoint():
    return admin_model.update_endpoint(request.json)

@app.route("/admin/endpoints", methods=["DELETE"])
def delete_endpoint():
    return admin_model.delete_endpoint(request.json)

@app.route("/admin/roles", methods=["POST"])
def create_role():
    return admin_model.create_role(request.json)

@app.route("/admin/roles", methods=["PUT"])
def update_role():
    return admin_model.update_role(request.json)

@app.route("/admin/roles", methods=["DELETE"])
def delete_role():
    return admin_model.delete_role(request.json)

