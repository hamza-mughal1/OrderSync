from app import app
from flask import request, make_response
from model.user_model import UserModel
from model.auth_model import AuthModel

# Initialize instances of the user and authentication models
user_model = UserModel()
auth_model = AuthModel()


# Route to handle user login requests
@app.route("/users/login", methods=["POST"])
def user_login():
    # Verify the user's credentials using data from the request and return a response
    return user_model.verify_user(request.json)


# Route to handle JWT refresh requests
@app.route("/users/refresh", methods=["POST"])
def refresh_jwt():
    # Refresh the JWT token for the user
    return user_model.refresh_jwt()


# Route to handle user logout requests
@app.route("/users/logout", methods=["POST"])
def logout():
    # Log out the current user
    return user_model.logout()


# Route to handle logout requests for all sessions
@app.route("/users/logout-all", methods=["POST"])
def logout_all():
    # Log out the user from all active sessions
    return user_model.logout_all()


# Route to handle user creation requests
@app.route("/users/users", methods=["POST"])
@auth_model.token_auth()  # Requires token authentication
def create_user():
    # Create a new user using data from the request
    return user_model.create_user(request.json)


# Route to handle user deletion requests
@app.route("/users/users", methods=["DELETE"])
@auth_model.token_auth()  # Requires token authentication
def delete_user():
    # Delete a user using data from the request
    return user_model.delete_user(request.json)
