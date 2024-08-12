from app import app
from model.information_model import InformationModel
from model.auth_model import AuthModel


information_model = InformationModel()
auth_model = AuthModel()


@app.route("/information/all-roles", methods=["GET"])
@auth_model.token_auth()
def all_roles():
    return information_model.all_roles()


@app.route("/information/all-endpoints", methods=["GET"])
@auth_model.token_auth()
def all_endpoints():
    return information_model.all_endpoints()
