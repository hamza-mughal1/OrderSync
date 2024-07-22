import mysql.connector
from model.config import *
import bcrypt
from datetime import datetime, timedelta
import jwt
from flask import make_response


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
            15)
        
        return {"token":token}, 200
