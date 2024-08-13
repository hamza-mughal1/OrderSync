import mysql.connector
from model.config import *
from flask import make_response, request
import re
import jwt
from model.mysql_connector_obj import create_connection


class InformationModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

        self.page_limit = 20

    @staticmethod
    def has_required_pairs(dictionary, required):
        return all(item in dictionary.keys() for item in required.keys())

    def all_roles(self):
        self.mycursor.execute("SELECT role FROM roles")
        return {"ROLES": list(map(lambda x: x["role"], self.mycursor.fetchall()))}

    def all_endpoints(self):
        authorization = request.headers.get("Authorization")
        try:
            if re.match("^Bearer *([^ ]+) *$", authorization, flags=0) == None:
                return make_response({"ERROR": "INVALID_TOKEN"}, 401)
        except TypeError:
            return make_response({"ERROR": "TOKEN NOT FOUND"}, 400)
        _, jwt_token = authorization.split(" ")

        token_data = jwt.decode(jwt_token, secret_key, algorithms="HS256")

        self.mycursor.execute(
            "SELECT endpoint, method FROM endpoints WHERE JSON_CONTAINS(role, %s)",
            (str(token_data["payload"]["role"]),),
        )

        return make_response(
            {
                "ENDPOINTS": [
                    {"endpoint": i["endpoint"], "method": list(i["method"])[0]}
                    for i in self.mycursor.fetchall()
                ]
            },
            200,
        )
