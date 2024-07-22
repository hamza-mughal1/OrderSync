import mysql.connector
from model.config import *
import jwt
from flask import request, make_response
import re
import json
from functools import wraps


class AuthModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"],
        )
        self.mycursor = self.db.cursor(dictionary=True)

    def token_auth(self, endpoint=""):
        def decorator(func):
            @wraps(func)
            def wrapper(*args):
                endpoint = request.url_rule
                authorization = request.headers.get("authorization")
                if re.match("^Bearer *([^ ]+) *$", authorization, flags=0) == False:
                    return make_response({"ERROR": "INVALID_TOKEN"}, 401)

                token = authorization.split(" ")[1]
                try:
                    tokendata = jwt.decode(token, secret_key, algorithms="HS256")
                except Exception as e:
                    return make_response({"ERROR": str(e)}, 401)

                role = tokendata["payload"]["role"]
                self.mycursor.execute(
                    f"SELECT role FROM ENDPOINTS WHERE ENDPOINT = '{endpoint}'"
                )
                roles = self.mycursor.fetchall()[0]["role"]
                roles = json.loads(roles)
                if (role in roles) == False:
                    return make_response({"ERROR": "Forbidden"}, 403)

                return func(*args)

            return wrapper

        return decorator
