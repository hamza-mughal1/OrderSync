from app import app
from model.information_model import InformationModel
from model.auth_model import AuthModel

# Initialize instances of the information and authentication models
information_model = InformationModel()
auth_model = AuthModel()


# Route to retrieve all roles
@app.route("/information/all-roles", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def all_roles():
    # Return a list of all roles from the information model
    return information_model.all_roles()


# Route to retrieve all endpoints
@app.route("/information/all-endpoints", methods=["GET"])
@auth_model.token_auth()  # Requires token authentication
def all_endpoints():
    # Return a list of all endpoints from the information model
    return information_model.all_endpoints()
