from app import app
from flask import request
from model.admin_model import AdminModel
from model.auth_model import AuthModel

# Initialize instances of the admin and authentication models
admin_model = AdminModel()
auth_model = AuthModel()


# Route to handle the creation of a new endpoint
@app.route("/admin/endpoints", methods=["POST"])
def create_endpoint():
    # Create a new endpoint using data from the request
    return admin_model.create_endpoint(request.json)


# Route to handle updating an existing endpoint
@app.route("/admin/endpoints", methods=["PUT"])
def update_endpoint():
    # Update an existing endpoint using data from the request
    return admin_model.update_endpoint(request.json)


# Route to handle deletion of an endpoint
@app.route("/admin/endpoints", methods=["DELETE"])
def delete_endpoint():
    # Delete an endpoint using data from the request
    return admin_model.delete_endpoint(request.json)


# Route to handle the creation of a new role
@app.route("/admin/roles", methods=["POST"])
def create_role():
    # Create a new role using data from the request
    return admin_model.create_role(request.json)


# Route to handle updating an existing role
@app.route("/admin/roles", methods=["PUT"])
def update_role():
    # Update an existing role using data from the request
    return admin_model.update_role(request.json)


# Route to handle deletion of a role
@app.route("/admin/roles", methods=["DELETE"])
def delete_role():
    # Delete a role using data from the request
    return admin_model.delete_role(request.json)
