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

        self.jwt_time_in_minutes = 15
        self.refresh_token_time_in_days = 2

    @staticmethod
    def generate_hashed_password(password):
        """
        Generate a hashed password with a salt.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

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
        if len(data := self.mycursor.fetchall())<1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)

        if data[0]["jwt_token"] != jwt_token:
            return make_response({"ERROR WITH JWT": "INVALID_TOKEN"}, 401)

        self.mycursor.execute("DELETE FROM available_refresh_token WHERE token = %s", (refresh_token,))
        
        tokendata = tokendata["payload"]
        self.mycursor.execute("SELECT id, user_role as role FROM users WHERE user_name = %s", (tokendata["user_name"],))
        data = self.mycursor.fetchall()[0]
        token = UserModel.generate_JWT({
            "user_name":tokendata["user_name"],
            "id":data["id"],
            "role":data["role"],
            "created_at":str(datetime.now()).split(".")[0],
            "token_role":"access-token"},
            self.jwt_time_in_minutes)
        
        refresh_token = UserModel.generate_JWT({
            "user_name":tokendata["user_name"],
            "id":data["id"],
            "role":data["role"],
            "token_role":"refresh-token"},
            self.refresh_token_time_in_days*1440)
    
        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role, jwt_token) values (%s, %s, %s, %s, %s)"
        self.mycursor.execute(q, (refresh_token, tokendata["user_name"],tokendata["id"],tokendata["role"],token))
        self.db.commit()

        return {"token":token,
                "refresh-token":refresh_token}, 200

    def verify_user(self, user_details):
        re_fields = {"user_name": "--", "password": "--"}
        
        if not UserModel.has_required_pairs(user_details, re_fields):
            return "Unauthorized", 401
        
        query = "SELECT password FROM users WHERE user_name = %s"
        self.mycursor.execute(query, (user_details["user_name"],))
        result = self.mycursor.fetchall()
        
        if len(result)<1:
            return "Login failed: Wrong username or password", 401
        
        result = result[0]
        if not bcrypt.checkpw(user_details["password"].encode("utf-8"), result["password"].encode("utf-8")):
            return "Login failed: Wrong username or password", 401

        self.mycursor.execute("SELECT id, user_role FROM users WHERE user_name = %s", (user_details["user_name"],))
        result = self.mycursor.fetchall()[0]
        token = UserModel.generate_JWT({
            "user_name":user_details["user_name"],
            "id":result["id"],
            "role":result["user_role"],
            "created_at":str(datetime.now()).split(".")[0],
            "token_role":"access-token"},
            self.jwt_time_in_minutes)
        
        refresh_token = UserModel.generate_JWT({
            "user_name":user_details["user_name"],
            "id":result["id"],
            "role":result["user_role"],
            "token_role":"refresh-token"},
            self.refresh_token_time_in_days*1440)
        
        q = "INSERT INTO available_refresh_token (token, user_name, user_id, user_role, jwt_token) values (%s, %s, %s, %s,%s)"
        self.mycursor.execute(q, (refresh_token, user_details["user_name"], result["id"], result["user_role"],token))
        self.db.commit()

        return {"token":token,
                "refresh-token":refresh_token}, 200

    def logout(self):
        authorization = request.headers.get("Authorization")
        if re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0) == None:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)
        
        _, jwt_token, _, refresh_token = authorization.split(" ")

        try:
            jwt_tokendata = jwt.decode(jwt_token, secret_key, algorithms="HS256")
        except Exception as e:
            return make_response({"ERROR WITH JWT TOKEN": str(e)}, 401)

        try:
            refresh_tokendata = jwt.decode(refresh_token, secret_key, algorithms="HS256")
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH REFRESH TOKEN": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH REFRESH TOKEN": str(e)}, 401)
        
        if refresh_tokendata["payload"]["id"] != jwt_tokendata["payload"]["id"]:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        self.mycursor.execute("SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,))
        if len(self.mycursor.fetchall())<1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)
        
        jwt_tokendata = jwt_tokendata["payload"]
        self.mycursor.execute("DELETE FROM available_refresh_token WHERE token = %s", (refresh_token,))
        self.db.commit()
        self.mycursor.execute("INSERT INTO blacklisted_token (token, user_id, role, created_at) value (%s, %s, %s, %s)", (jwt_token, jwt_tokendata["id"], jwt_tokendata["role"], jwt_tokendata["created_at"]))
        self.db.commit()
        return make_response({"MESSAGE":"YOU HAVE LOGGED OUT SUCCESSFULLY"}, 200)
    
    def logout_all(self):
        authorization = request.headers.get("Authorization")
        if re.match("^Bearer *([^ ]+) *Refresh *([^ ]+) *$", authorization, flags=0) == None:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)
        
        _, jwt_token, _, refresh_token = authorization.split(" ")

        try:
            jwt_tokendata = jwt.decode(jwt_token, secret_key, algorithms="HS256")
        except Exception as e:
            return make_response({"ERROR WITH JWT TOKEN": str(e)}, 401)

        try:
            refresh_tokendata = jwt.decode(refresh_token, secret_key, algorithms="HS256")
        except jwt.exceptions.DecodeError:
            return make_response({"ERROR WITH REFRESH TOKEN": "INVALID_TOKEN"}, 401)
        except Exception as e:
            return make_response({"ERROR WITH REFRESH TOKEN": str(e)}, 401)
        
        if refresh_tokendata["payload"]["id"] != jwt_tokendata["payload"]["id"]:
            return make_response({"ERROR": "INVALID_TOKEN"}, 401)

        self.mycursor.execute("SELECT * FROM available_refresh_token WHERE token = %s", (refresh_token,))
        if len(self.mycursor.fetchall())<1:
            return make_response({"ERROR WITH REFRESH TOKEN": "BLACKLISTED TOKEN"}, 401)
        
        jwt_tokendata = jwt_tokendata["payload"]
        self.mycursor.execute("SELECT jwt_token FROM available_refresh_token WHERE user_id = %s", (jwt_tokendata["id"],))
        for i in self.mycursor.fetchall():
            self.mycursor.execute("INSERT INTO blacklisted_token (token, user_id, role, created_at) value (%s, %s, %s, %s)", (i["jwt_token"], jwt_tokendata["id"], jwt_tokendata["role"], jwt_tokendata["created_at"]))
        self.db.commit()
        self.mycursor.execute("DELETE FROM available_refresh_token WHERE user_id = %s", (jwt_tokendata["id"],))
        self.db.commit()
        return make_response({"MESSAGE":"YOU HAVE LOGGED OUT SUCCESSFULLY"}, 200)

    def create_user(self, user_details):
        re_fields = {"user_name":"--", "name":"--", "password":"--", "user_role":"--"}
        
        if not UserModel.has_required_pairs(user_details, re_fields):
            return "Unauthorized", 401
        try:
            hashed_pass = UserModel.generate_hashed_password(user_details["password"])
        except (KeyError, TypeError):
            return make_response({"ERROR":"INCORRECT PARAMETERS"}, 400)
        except:
            return make_response({"ERROR":"INTERNAL SERVER ERROR"}, 500)

        try:
            self.mycursor.execute("INSERT INTO users (name, user_name, password, user_role) value (%s, %s, %s, %s)", (user_details["name"], user_details["user_name"], hashed_pass, user_details["user_role"]))
            self.db.commit()
            return make_response({"MESSAGE":"USER HAS BEEN REGISTERED SUCCESSFULLY"}, 201)
        except mysql.connector.errors.IntegrityError:
            return make_response({"ERROR":"USERNAME ALREADY EXISTS"}, 409)
        
    def delete_user(self, user_details):
        re_fields = {"user_name":"--"}
        
        if not UserModel.has_required_pairs(user_details, re_fields):
            return "Unauthorized", 401
        
        self.mycursor.execute("SELECT id FROM users WHERE user_name = %s",(user_details["user_name"],))
        if len(id := self.mycursor.fetchall())<1:
            return make_response({"MESSAGE":"NO USER FOUND"}, 400)
        
        self.mycursor.execute("SELECT id FROM sales WHERE user_id = (SELECT id FROM users WHERE user_name = %s)",(user_details["user_name"],))
        all_sales = self.mycursor.fetchall()
        for i in all_sales:
            self.mycursor.execute("DELETE FROM sale_details WHERE sale_id = %s", (i["id"],))

        self.db.commit()
        self.mycursor.execute("DELETE FROM sales WHERE user_id = %s",(id[0]["id"],))
        self.mycursor.execute("DELETE FROM users WHERE user_name = %s", (user_details["user_name"],))
        self.db.commit()
        return make_response({"MESSAGE":"USER HAS BEEN DELETED SUCCESSFULLY"}, 200)
    
