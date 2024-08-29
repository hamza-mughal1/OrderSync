from model.config import *
from flask import make_response
import json
from model.mysql_connector_obj import create_connection


class AdminModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

    @staticmethod
    def has_required_pairs(dictionary, required):
        """
        Check if the dictionary contains all required keys.

        :param dictionary: The dictionary to check.
        :param required: A dictionary of required keys.
        :return: True if all required keys are present, False otherwise.
        """
        return all(item in dictionary.keys() for item in required.keys())

    def create_endpoint(self, endpoint_data):
        """
        Create a new endpoint in the database.

        :param endpoint_data: A dictionary containing endpoint information.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {"endpoint": "--", "method": "--", "roles": "--"}

        if not type(endpoint_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        try:
            endpoint_list = json.loads(endpoint_data["roles"].replace("'", '"'))
        except:
            return make_response({"ERROR": "'ROLES' MUST BE A LIST/ARRAY"}, 401)

        final_endpoints = []
        for i in endpoint_list:
            self.mycursor.execute("SELECT id FROM roles WHERE role = %s", (i,))
            if len(data := self.mycursor.fetchall()) < 1:
                return make_response({"ERROR": "ROLE NOT FOUND"}, 401)
            final_endpoints.append(data[0]["id"])

        self.mycursor.execute(
            "SELECT * FROM endpoints WHERE endpoint = %s AND method = %s",
            (endpoint_data["endpoint"], endpoint_data["method"]),
        )
        if len(self.mycursor.fetchall()) >= 1:
            return make_response({"ERROR": "ENDPOINT ALREADY EXISTS"}, 409)
        try:
            self.mycursor.execute(
                "INSERT INTO endpoints (endpoint, method, role) VALUE (%s,%s,%s)",
                (
                    endpoint_data["endpoint"],
                    endpoint_data["method"],
                    str(final_endpoints),
                ),
            )
            self.db.commit()
        except:
            return make_response({"ERROR": "INVALID PARAMETERS"}, 400)

        return make_response({"MESSAGE": "ENDPOINT HAS BEEN ADDED SUCCESSFULLY"}, 201)

    def update_endpoint(self, endpoint_data):
        """
        Update an existing endpoint in the database.

        :param endpoint_data: A dictionary containing the updated endpoint information.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "old_endpoint": "--",
            "endpoint": "--",
            "method": "--",
            "roles": "--",
        }

        if not type(endpoint_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        try:
            endpoint_list = json.loads(endpoint_data["roles"].replace("'", '"'))
        except:
            return make_response({"ERROR": "'ROLES' MUST BE A LIST/ARRAY"}, 401)

        final_roles = []
        for i in endpoint_list:
            self.mycursor.execute("SELECT id FROM roles WHERE role = %s", (i,))
            if len(data := self.mycursor.fetchall()) < 1:
                return make_response({"ERROR": "ROLE NOT FOUND"}, 401)
            final_roles.append(data[0]["id"])

        try:
            self.mycursor.execute(
                "UPDATE endpoints SET endpoint = %s, method = %s, role = %s WHERE endpoint = %s ",
                (
                    endpoint_data["endpoint"],
                    endpoint_data["method"],
                    str(final_roles),
                    endpoint_data["old_endpoint"],
                ),
            )
            self.db.commit()
        except:
            return make_response({"ERROR": "INVALID PARAMETERS"}, 400)

        return make_response({"MESSAGE": "ENDPOINT HAS BEEN UPDATED SUCCESSFULLY"}, 201)

    def delete_endpoint(self, endpoint_data):
        """
        Delete an endpoint from the database.

        :param endpoint_data: A dictionary containing the endpoint information to delete.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "endpoint": "--",
        }

        if not type(endpoint_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(endpoint_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        self.mycursor.execute(
            "SELECT * FROM endpoints WHERE endpoint = %s", (endpoint_data["endpoint"],)
        )
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "ENDPOINT NOT FOUND"}, 404)

        self.mycursor.execute(
            "DELETE FROM endpoints WHERE endpoint = %s", (endpoint_data["endpoint"],)
        )
        self.db.commit()

        return make_response({"MESSAGE": "'ENDPOINT' HAS BEEN DELETED"}, 200)

    def create_role(self, role_data):
        """
        Create a new role in the database.

        :param role_data: A dictionary containing role information.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "role": "--",
        }

        if not type(role_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON/DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        self.mycursor.execute(
            "SELECT * FROM roles WHERE role = %s", (role_data["role"],)
        )
        if len(self.mycursor.fetchall()) >= 1:
            return make_response({"ERROR": "ROLE ALREADY EXISTS"}, 209)

        self.mycursor.execute(
            "INSERT INTO roles (role) value (%s)", (role_data["role"],)
        )
        self.db.commit()

        return make_response({"MESSAGE": "'ROLE' HAS BEEN ADDED SUCCESSFULLY"}, 201)

    def update_role(self, role_data):
        """
        Update an existing role in the database.

        :param role_data: A dictionary containing the updated role information.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "old_role": "--",
            "role": "--",
        }

        if not type(role_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        self.mycursor.execute(
            "SELECT * FROM roles WHERE role = %s", (role_data["old_role"],)
        )
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "ROLE NOT FOUND"}, 404)

        self.mycursor.execute(
            "UPDATE roles SET role = %s WHERE role = %s",
            (role_data["role"], role_data["old_role"]),
        )
        self.db.commit()

        return make_response({"MESSAGE": "'ROLE' HAS BEEN UPDATED SUCCESSFULLY"}, 200)

    def delete_role(self, role_data):
        """
        Delete a role from the database.

        :param role_data: A dictionary containing the role information to delete.
        :return: A response indicating the success or failure of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "role": "--",
        }

        if not type(role_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON/DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(role_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        self.mycursor.execute(
            "SELECT * FROM roles WHERE role = %s", (role_data["role"],)
        )
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "ROLE NOT FOUND"}, 404)

        self.mycursor.execute("DELETE FROM roles WHERE role = %s", (role_data["role"],))

        return make_response({"MESSAGE": "'ROLE' HAS BEEN DELETED SUCCESSFULLY"}, 200)

    def create_category(self, category_data):
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "category_name": "--",
        }

        if not type(category_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON/DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(category_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        self.mycursor.execute("INSERT INTO categories (name) VALUES (%s)", (category_data["category_name"]))

        return make_response({"MESSAGE": "'category' HAS BEEN ADDED SUCCESSFULLY"}, 201)

    def delete_category(self, category_data):
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "category_name": "--",
        }

        if not type(category_data) == dict:
            return make_response(
                {"ERROR": "ONLY JSON/DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not AdminModel.has_required_pairs(category_data, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)
        
    
        self.mycursor.execute("SELECT id FROM categories WHERE name = %s", (category_data["category_name"],))
        if len(data := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR":"NO CATEGORY FOUND"}, 404)
        self.mycursor.execute("SELECT id FROM products WHERE category_id = %s",(data[0]["id"],))
        for i in self.mycursor.fetchall():
            try:
                self.mycursor.execute(
                    "SELECT sale_id, price, discount_price FROM sale_details where product_id = %s",
                    (i["id"],),
                )
                result = self.mycursor.fetchall()
                self.mycursor.execute(
                    "DELETE FROM sale_details WHERE product_id = %s", (id,)
                )
                for i in result:
                    self.mycursor.execute(
                        "UPDATE sales SET price = price - %s where id = %s",
                        (i["price"], i["sale_id"]),
                    )
                    self.db.commit()
                    self.mycursor.execute(
                        "SELECT price, discount from sales where id = %s", (i[0],)
                    )
                    price = self.mycursor.fetchall()[0]["price"]
                    discount_per = self.mycursor.fetchall()[0]["discount"]
                    discount_price = price * (discount_per / 100)
                    self.mycursor.execute(
                        "UPDATE sales SET discount_price = %s where id = %s",
                        (discount_price, i[0]),
                    )
                    self.db.commit()
            except:
                return make_response({"ERROR": "INTERNAL SERVER ERROR"}, 500)
            self.mycursor.execute("DELETE FROM products WHERE id = %s", (id,))
            self.db.commit()
        self.mycursor.execute("DELETE from categories WHERE id = %s", (data[0]["id"],))
        self.db.commit()
        return make_response({"MESSAGE":"CATEGORY HAS BEEN DELETED SUCCESSFULLY"}, 200)


    # -----------------------
    # NO PURPOSE TO USE
    # -----------------------
    # def delete_endpoint_by_id(self, endpoint_data):
    #     re_fields= {
    #         "id": "--",
    #         }

    #     if not AdminModel.has_required_pairs(endpoint_data, re_fields):
    #         return make_response({"ERROR":"UNAUTHORIZED"}, 401)

    #     self.mycursor.execute("DELETE FROM endpoints WHERE id = %s",(endpoint_data["id"],))
    #     self.db.commit()

    #     return make_response({"MESSAGE":"'ENDPOINT' HAS BEEN DELETED"}, 200)
