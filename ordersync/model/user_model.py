import mysql.connector
from model.config import *
import bcrypt
from datetime import datetime, timedelta
import jwt
from flask import make_response, request
import re

class UserModel:
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

        self.jwt_time_in_minutes = 1
        self.refresh_token_time_in_days = 2

    @staticmethod
    def has_required_pairs(dictionary, required):
        return all(item in dictionary.keys() for item in required.keys())
    
    @staticmethod
    def generate_JWT(data, exp_time_limit_in_minutes):
        exp_time = datetime.now() + timedelta(minutes=exp_time_limit_in_minutes)
        exp_epoch_time = int(exp_time.timestamp())
        payload = {
            "payload":data,
            "exp":exp_epoch_time
        }

        return jwt.encode(payload, secret_key, algorithm="HS256")


    def refresh_jwt(self):
        authorization = request.headers.get("Authorization")
        if re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0) == None:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)
        
        _, jwt_token, _, refresh_token = authorization.split(" ")

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

        self.mycursor.execute("SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,))
        if len(self.mycursor.fetchall())<1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)
        

        self.mycursor.execute("DELETE FROM available_refresh_token WHERE token = %s", (refresh_token,))

        tokendata = tokendata["payload"]
        token = UserModel.generate_JWT({
            "user_name":tokendata["user_name"],
            "id":tokendata["id"],
            "role":tokendata["role"]},
            self.jwt_time_in_minutes)
        
        refresh_token = UserModel.generate_JWT({
            "user_name":tokendata["user_name"],
            "id":tokendata["id"],
            "role":tokendata["role"]},
            self.refresh_token_time_in_days*1440)
    
        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role) values (%s, %s, %s, %s)"
        self.mycursor.execute(q, (refresh_token, tokendata["user_name"],tokendata["id"],tokendata["role"],))
        self.db.commit()

        return {"jwt-token":token,
                "refresh-token":refresh_token}, 200

    def verify_user(self, user_details):
        re_fields = {"user_name": "--", "password": "--"}
        
        if UserModel.has_required_pairs(user_details, re_fields) == False:
            return "Unauthorized", 401
        
        query = "SELECT password FROM users WHERE user_name = %s"
        self.mycursor.execute(query, (user_details["user_name"],))
        result = self.mycursor.fetchall()
        
        if len(result)<1:
            return "Login failed: Wrong username or password", 401
        
        result = result[0]
        if bcrypt.checkpw(user_details["password"].encode("utf-8"), result["password"].encode("utf-8")) == False:
            return "Login failed: Wrong username or password", 401

        self.mycursor.execute(f"SELECT id, user_role FROM users WHERE user_name = '{user_details["user_name"]}'")
        result = self.mycursor.fetchall()[0]
        token = UserModel.generate_JWT({
            "user_name":user_details["user_name"],
            "id":result["id"],
            "role":result["user_role"]},
            self.jwt_time_in_minutes)
        
        refresh_token = UserModel.generate_JWT({
            "user_name":user_details["user_name"],
            "id":result["id"],
            "role":result["user_role"]},
            self.refresh_token_time_in_days)
        
        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role) values (%s, %s, %s, %s)"
        self.mycursor.execute(q, (refresh_token, user_details["user_name"], result["id"], result["user_role"],))
        self.db.commit()

        return {"jwt-token":token,
                "refresh-token":refresh_token}, 200
