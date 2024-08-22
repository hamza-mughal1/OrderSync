from model.config import *
import jwt
from flask import request, make_response
import re
import json
from functools import wraps
from model.mysql_connector_obj import create_connection


class AuthModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

    def token_auth(self, endpoint=""):
        """
        Decorator function to handle token-based authentication for endpoints.

        Args:
            endpoint (str): The endpoint for which authentication is to be applied. Defaults to an empty string.

        Returns:
            decorator: A decorator that wraps the view function for token authentication.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        ed = endpoint

        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # Determine the endpoint to be authenticated
                if ed == "":
                    endpoint = request.url_rule
                else:
                    endpoint = ed

                # Get the authorization header from the request
                authorization = request.headers.get("authorization")
                try:
                    # Check if the authorization header follows the Bearer token format
                    if re.match("^Bearer *([^ ]+) *$", authorization, flags=0) == None:
                        return make_response({"ERROR": "INVALID_TOKEN"}, 401)
                except TypeError:
                    return make_response({"ERROR": "TOKEN NOT FOUND"}, 400)

                # Extract the token from the authorization header
                token = authorization.split(" ")[1]
                try:
                    # Decode the token using JWT
                    tokendata = jwt.decode(token, secret_key, algorithms="HS256")
                except Exception as e:
                    return make_response({"ERROR": str(e).upper()}, 401)

                # Verify that the token role is 'access-token'
                if tokendata["payload"]["token_role"] != "access-token":
                    return make_response({"ERROR": "Forbidden"}, 403)

                role = tokendata["payload"]["role"]
                self.mycursor.execute(
                    "SELECT role, method FROM ENDPOINTS WHERE ENDPOINT = %s",
                    (str(endpoint),),
                )
                data = self.mycursor.fetchall()
                if len(data) < 1:
                    return make_response({"ERROR": "NO ENDPOINT FOUND"}, 404)
                data = data[0]
                roles = data["role"]
                roles = json.loads(roles)

                # Check if the role is permitted for the requested endpoint
                if (role in roles) == False:
                    return make_response({"ERROR": "Forbidden"}, 403)

                # Check if the request method is allowed for the endpoint
                if request.method == data["method"]:
                    return make_response({"ERROR": "Forbidden"}, 403)

                # Check if the token is blacklisted
                self.mycursor.execute(
                    "SELECT * FROM blacklisted_token WHERE token = %s", (token,)
                )
                if len(self.mycursor.fetchall()) >= 1:
                    return make_response({"ERROR": "Forbidden"}, 403)

                return func(*args, **kwargs)

            return wrapper

        return decorator
