import mysql.connector
from model.config import *
from flask import make_response
import json

class AdminModel:
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

    def add_endpoint(self, endpoint_data): 
        re_fields= {
            "endpoint": "--",
            "method": "--",
            "roles": "--"
            }
        
        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        try:
            endpoint_list = json.loads(endpoint_data["roles"].replace("'","\""))
        except:
            return make_response({"ERROR":"'ROLES' MUST A LIST/ARRAY"}, 401)
        
        final_endpoints = []
        for i in endpoint_list:
            self.mycursor.execute("SELECT id FROM roles WHERE role = %s",(i,))
            if len(data := self.mycursor.fetchall())<1:
                make_response({"ERROR":"ROLE NOT FOUND"}, 401)
            final_endpoints.append(data[0]["id"])
        

        self.mycursor.execute("INSERT INTO endpoints (endpoint, method, role) VALUE (%s,%s,%s)", (endpoint_data["endpoint"],endpoint_data["method"],str(final_endpoints)))
        self.db.commit()

        return make_response({"MESSAGE":"ENDPOINT HAS BEEN ADDED SUCCESSFULLY"}, 201)
    
    def update_endpoint(self, endpoint_data): 
        re_fields= {
            "old_endpoint": "--",
            "endpoint": "--",
            "method": "--",
            "roles": "--"
            }
        
        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        try:
            endpoint_list = json.loads(endpoint_data["roles"].replace("'","\""))
        except:
            return make_response({"ERROR":"'ROLES' MUST BE A LIST/ARRAY"}, 401)
        
        final_endpoints = []
        for i in endpoint_list:
            self.mycursor.execute("SELECT id FROM roles WHERE role = %s",(i,))
            if len(data := self.mycursor.fetchall())<1:
                make_response({"ERROR":"ROLE NOT FOUND"}, 401)
            final_endpoints.append(data[0]["id"])
        

        self.mycursor.execute("UPDATE endpoints SET endpoint = %s, method = %s, role = %s WHERE endpoint = %s ", (endpoint_data["endpoint"],endpoint_data["method"],str(final_endpoints), re_fields["old_endpoint"]))
        self.db.commit()

        return make_response({"MESSAGE":"ENDPOINT HAS BEEN UPDATED SUCCESSFULLY"}, 201)
    
    def delete_endpoint_by_name(self, endpoint_data): 
        re_fields= {
            "endpoint": "--",
            }
        
        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        self.mycursor.execute("DELETE FROM endpoints WHERE endpoint = %s",(endpoint_data["endpoint"],))
        self.db.commit()

        return make_response({"MESSAGE":"'ENDPOINT' HAS BEEN DELETED"}, 200)
    
    def delete_endpoint_by_id(self, endpoint_data): 
        re_fields= {
            "id": "--",
            }
        
        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        self.mycursor.execute("DELETE FROM endpoints WHERE id = %s",(endpoint_data["id"],))
        self.db.commit()

        return make_response({"MESSAGE":"'ENDPOINT' HAS BEEN DELETED"}, 200)
    
    def create_role(self, role_data):
        re_fields= {
            "role": "--",
            }
        
        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        self.mycursor.execute("INSERT INTO roles (role) value (%s)",(role_data["role"],))
        self.db.commit()

        return make_response({"MESSAGE":"'ROLE' HAS BEEN ADDED SUCCESSFULLY"}, 201)
    
    def update_role(self, role_data):
        re_fields= {
            "old_role": "--",
            "role": "--",
            }
        
        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        self.mycursor.execute("UPDATE roles SET role = %s WHERE role = %s",(role_data["role"], role_data["old_role"]))
        self.db.commit()

        return make_response({"MESSAGE":"'ROLE' HAS BEEN UPDATED SUCCESSFULLY"}, 200)
    
    def remove_role(self, role_data):
        re_fields= {
            "role": "--",
            }
        
        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        

        self.mycursor.execute("DELETE FROM roles WHERE role = %s",(role_data["role"],))

        return make_response({"MESSAGE":"'ROLE' HAS BEEN DELETED SUCCESSFULLY"}, 200)
    
