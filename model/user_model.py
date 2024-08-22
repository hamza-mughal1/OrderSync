from flask import make_response, request
import jwt
import re
import bcrypt
from datetime import datetime, timedelta
from model.config import *

"""
Import 'create_connection' function from 'mysql_connector_obj' file to create a connection to the database,
to maintain the connection only from one place in all models
"""
from model.mysql_connector_obj import create_connection


class UserModel:
    def __init__(self):
        """
        UserModel: A class which handles all the functionality related to users.
        """

        # Create connection with the database
        self.db = create_connection()
        self.mycursor = self.db.cursor(
            dictionary=True
        )  # Create cursor to perform operations in the DB. (dictionary=True) to retreive the data in dict format

        # Acess and refresh token expiration time
        self.jwt_time_in_minutes = 15
        self.refresh_token_time_in_days = 2

    @staticmethod
    def generate_hashed_password(password):
        """
        Generate a hashed password with a random salt.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
        return hashed_password.decode("utf-8")

    @staticmethod
    def has_required_pairs(dictionary, required):
        """
        Check if the dict has required keys.
        Return: True or Falses
        """
        return all(item in dictionary.keys() for item in required.keys())

    @staticmethod
    def generate_JWT(data, exp_time_limit_in_minutes):
        """
        Generate JWT token with given data and expiration time
        args:
            data- (type: dict) data to attach in the JWT
            exp... - (type: int) time (in minutes) for the exp of the token
        return:
            JWT token (type: bytes)
        """
        exp_time = datetime.now() + timedelta(minutes=exp_time_limit_in_minutes)
        exp_epoch_time = int(exp_time.timestamp())
        payload = {"payload": data, "exp": exp_epoch_time}

        return jwt.encode(payload, secret_key, algorithm="HS256")

    def refresh_jwt(self):
        """
        Check if the acess token has expired then returns a new refresh and acess token.
        features:
            Token rotation: create new refresh and acess token every time called to make the connection more secure
            and to make the connection long live till user is active. (Reset the time back to default)
            Acess token check: check if the current access token is valid then don't return new tokens
        return:
            New refresh and acess token (type JSON) containing both tokens
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        # Read header of the request and fetch tokens if available
        authorization = request.headers.get("Authorization")
        if (
            re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0)
            == None
        ):
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        _, jwt_token, _, refresh_token = authorization.split(" ")

        # Check if acess and refresh tokens are correct and are valid
        try:
            jwt.decode(jwt_token, secret_key, algorithms="HS256")
            return make_response({"ERROR": "CURRENT JWT IS STILL VALID"}, 400)
        except jwt.ExpiredSignatureError:
            pass
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH JWT": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH JWT TOKEN": str(e)}, 401)

        try:
            tokendata = jwt.decode(refresh_token, secret_key, algorithms="HS256")
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH REFRESH TOKEN": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH REFRESH TOKEN": str(e)}, 401)

        # Check if refresh token is not black listed (not available in the DB)
        self.mycursor.execute(
            "SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,)
        )
        if len(data := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)

        # Check if the access token is the same as in the DB, which was given with the current refresh token
        if data[0]["jwt_token"] != jwt_token:
            return make_response({"ERROR WITH JWT": "INVALID_TOKEN"}, 401)

        # Delete tokens from the DB if everything is fine and generating new tokens
        self.mycursor.execute(
            "DELETE FROM available_refresh_token WHERE token = %s", (refresh_token,)
        )

        tokendata = tokendata["payload"]
        self.mycursor.execute(
            "SELECT id, user_role as role FROM users WHERE user_name = %s",
            (tokendata["user_name"],),
        )
        data = self.mycursor.fetchall()[0]
        token = UserModel.generate_JWT(
            {
                "user_name": tokendata["user_name"],
                "id": data["id"],
                "role": data["role"],
                "created_at": str(datetime.now()).split(".")[0],
                "token_role": "access-token",
            },
            self.jwt_time_in_minutes,
        )

        refresh_token = UserModel.generate_JWT(
            {
                "user_name": tokendata["user_name"],
                "id": data["id"],
                "role": data["role"],
                "token_role": "refresh-token",
            },
            self.refresh_token_time_in_days * 1440,
        )

        # Insert new tokens in to the DB
        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role, jwt_token) values (%s, %s, %s, %s, %s)"
        self.mycursor.execute(
            q,
            (
                refresh_token,
                tokendata["user_name"],
                tokendata["id"],
                tokendata["role"],
                token,
            ),
        )
        self.db.commit()

        # Return new tokens
        return make_response({"token": token, "refresh-token": refresh_token}, 200)

    def verify_user(self, user_details):
        """
        Login user
        Check if the credentials are correct then return refresh and access tokens.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {"user_name": "--", "password": "--"}

        if not UserModel.has_required_pairs(user_details, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        query = "SELECT password FROM users WHERE user_name = %s"
        self.mycursor.execute(query, (user_details["user_name"],))
        result = self.mycursor.fetchall()

        # Check if user exists in the DB
        if len(result) < 1:
            return make_response(
                {"ERROR": "Login failed: Wrong username or password"}, 401
            )

        result = result[0]
        if not bcrypt.checkpw(
            user_details["password"].encode("utf-8"), result["password"].encode("utf-8")
        ):  # Check if the password is correct
            return make_response(
                {"ERROR": "Login failed: Wrong username or password"}, 401
            )

        self.mycursor.execute(
            "SELECT id, user_role FROM users WHERE user_name = %s",
            (user_details["user_name"],),
        )
        # Generate and return tokens
        result = self.mycursor.fetchall()[0]
        token = UserModel.generate_JWT(
            {
                "user_name": user_details["user_name"],
                "id": result["id"],
                "role": result["user_role"],
                "created_at": str(datetime.now()).split(".")[0],
                "token_role": "access-token",
            },
            self.jwt_time_in_minutes,
        )

        refresh_token = UserModel.generate_JWT(
            {
                "user_name": user_details["user_name"],
                "id": result["id"],
                "role": result["user_role"],
                "token_role": "refresh-token",
            },
            self.refresh_token_time_in_days * 1440,
        )

        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role, jwt_token) values (%s, %s, %s, %s,%s)"
        self.mycursor.execute(
            q,
            (
                refresh_token,
                user_details["user_name"],
                result["id"],
                result["user_role"],
                token,
            ),
        )
        # Commit to the DB to save the changes in the DB
        self.db.commit()

        return make_response({"token": token, "refresh-token": refresh_token}, 200)

    def logout(self):
        """
        Logout user using refresh and access token.
        algorithm: Delete access and refresh token from the DB, when the user try to use token next time he will be unable to,
        so he will have to login again.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        authorization = request.headers.get("Authorization")
        if (
            re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0)
            == None
        ):
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        _, jwt_token, _, refresh_token = authorization.split(" ")

        try:
            jwt_tokendata = jwt.decode(jwt_token, secret_key, algorithms="HS256")
        except Exception as e:
            return make_response({"ERROR WITH JWT TOKEN": str(e)}, 401)

        try:
            refresh_tokendata = jwt.decode(
                refresh_token, secret_key, algorithms="HS256"
            )
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH REFRESH TOKEN": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH REFRESH TOKEN": str(e)}, 401)

        if refresh_tokendata["payload"]["id"] != jwt_tokendata["payload"]["id"]:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        self.mycursor.execute(
            "SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,)
        )
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)

        jwt_tokendata = jwt_tokendata["payload"]
        self.mycursor.execute(
            "DELETE FROM available_refresh_token WHERE token = %s", (refresh_token,)
        )
        self.db.commit()
        self.mycursor.execute(
            "INSERT INTO blacklisted_token (token, user_id, role, created_at) value (%s, %s, %s, %s)",
            (
                jwt_token,
                jwt_tokendata["id"],
                jwt_tokendata["role"],
                jwt_tokendata["created_at"],
            ),
        )
        self.db.commit()
        return make_response({"MESSAGE": "YOU HAVE LOGGED OUT SUCCESSFULLY"}, 200)

    def logout_all(self):
        """
        Logout from all devices
        algorithm: Delete all tokens of the user from the DB
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        authorization = request.headers.get("Authorization")
        if (
            re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0)
            == None
        ):
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        _, jwt_token, _, refresh_token = authorization.split(" ")

        try:
            jwt_tokendata = jwt.decode(jwt_token, secret_key, algorithms="HS256")
        except Exception as e:
            return make_response({"ERROR WITH JWT TOKEN": str(e)}, 401)

        try:
            refresh_tokendata = jwt.decode(
                refresh_token, secret_key, algorithms="HS256"
            )
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH REFRESH TOKEN": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH REFRESH TOKEN": str(e)}, 401)

        if refresh_tokendata["payload"]["id"] != jwt_tokendata["payload"]["id"]:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        self.mycursor.execute(
            "SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,)
        )
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)

        jwt_tokendata = jwt_tokendata["payload"]
        self.mycursor.execute(
            "SELECT jwt_token FROM available_refresh_token WHERE user_id = %s",
            (jwt_tokendata["id"],),
        )
        for i in self.mycursor.fetchall():
            self.mycursor.execute(
                "INSERT INTO blacklisted_token (token, user_id, role, created_at) value (%s, %s, %s, %s)",
                (
                    i["jwt_token"],
                    jwt_tokendata["id"],
                    jwt_tokendata["role"],
                    jwt_tokendata["created_at"],
                ),
            )
        self.db.commit()
        self.mycursor.execute(
            "DELETE FROM available_refresh_token WHERE user_id = %s",
            (jwt_tokendata["id"],),
        )
        self.db.commit()
        return make_response({"MESSAGE": "YOU HAVE LOGGED OUT SUCCESSFULLY"}, 200)

    def create_user(self, user_details):
        """
        Create/register new user
        args: user_details (type: JSON)
                        fields:
                            {
                                "user_name": "--",
                                "name": "--",
                                "password": "--",
                                "user_role": "--",
                            }
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "user_name": "--",
            "name": "--",
            "password": "--",
            "user_role": "--",
        }

        if not type(user_details) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not UserModel.has_required_pairs(user_details, re_fields):
            return "Unauthorized", 401

        try:
            hashed_pass = UserModel.generate_hashed_password(user_details["password"])
        except (KeyError, TypeError):
            return make_response({"ERROR": "INCORRECT PARAMETERS"}, 400)
        except:
            return make_response({"ERROR": "INTERNAL SERVER ERROR"}, 500)

        self.mycursor.execute(
            "SELECT * FROM users WHERE user_name = %s", (user_details["user_name"],)
        )
        if len(self.mycursor.fetchall()) >= 1:
            return make_response({"ERROR": "USERNAME ALREADY EXISTS"}, 409)

        self.mycursor.execute(
            "SELECT id FROM roles WHERE role = %s", (user_details["user_role"],)
        )
        if len(id := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "ROLE NOT FOUND"}, 404)

        self.mycursor.execute(
            "INSERT INTO users (name, user_name, password, user_role) value (%s, %s, %s, %s)",
            (
                user_details["name"],
                user_details["user_name"],
                hashed_pass,
                id[0]["id"],
            ),
        )
        self.db.commit()
        return make_response({"MESSAGE": "USER HAS BEEN REGISTERED SUCCESSFULLY"}, 201)

    def delete_user(self, user_details):
        """
        Delete user
        args: user_details (type: JSON)
                        fields:
                            {
                                "user_name": "--"
                            }
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {"user_name": "--"}

        if not UserModel.has_required_pairs(user_details, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        if not UserModel.has_required_pairs(user_details, re_fields):
            return make_response({"ERROR": "Unauthorized"}, 401)

        self.mycursor.execute(
            "SELECT id FROM users WHERE user_name = %s", (user_details["user_name"],)
        )
        if len(id := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "NO USER FOUND"}, 400)

        self.mycursor.execute(
            "SELECT id FROM sales WHERE user_id = (SELECT id FROM users WHERE user_name = %s)",
            (user_details["user_name"],),
        )
        all_sales = self.mycursor.fetchall()
        for i in all_sales:
            self.mycursor.execute(
                "DELETE FROM sale_details WHERE sale_id = %s", (i["id"],)
            )

        self.db.commit()
        self.mycursor.execute("DELETE FROM sales WHERE user_id = %s", (id[0]["id"],))
        self.mycursor.execute(
            "DELETE FROM users WHERE user_name = %s", (user_details["user_name"],)
        )
        self.db.commit()
        return make_response({"MESSAGE": "USER HAS BEEN DELETED SUCCESSFULLY"}, 200)
