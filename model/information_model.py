from flask import make_response, request
import re
import jwt
from model.config import *

"""
Import 'create_connection' function from 'mysql_connector_obj' file to create a connection to the database,
to maintain the connection only from one place in all models
"""
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
        """
        Check if the dictionary contains all the required keys.

        Args:
            dictionary (dict): The dictionary to check.
            required (dict): A dictionary of required keys.

        Returns:
            bool: True if all required keys are present, False otherwise.
        """
        return all(item in dictionary.keys() for item in required.keys())

    def all_roles(self):
        """
        Retrieve all roles from the database.

        Returns:
            dict: A dictionary with a list of roles.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute("SELECT role FROM roles")
        return {"ROLES": list(map(lambda x: x["role"], self.mycursor.fetchall()))}

    def all_endpoints(self):
        """
        Retrieve all endpoints accessible to the user based on their role.

        Returns:
            Response: A Flask response object with a list of endpoints and HTTP status code.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
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
