import mysql.connector
from model.config import *
from flask import make_response, request
import jwt
import re
from model.mysql_connector_obj import create_connection


class OrderModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

    @staticmethod
    def has_required_pairs(dictionary, required):
        """
        Check if all required keys are present in the given dictionary.

        Args:
            dictionary (dict): The dictionary to check.
            required (dict): A dictionary where keys are required keys.

        Returns:
            bool: True if all required keys are present, otherwise False.
        """
        return all(item in dictionary.keys() for item in required.keys())

    def place_order(self, sale_details):
        """
        Place a new order based on the provided sale details.

        Args:
            sale_details (dict): A dictionary containing sale information and products.

        Returns:
            flask.Response: A response object indicating the result of the operation.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "products": "--",
            "sale_discount_per": "--",
            "sale_discount_desc": "--",
        }

        # Check if sale_details is a dictionary and has required fields
        if not type(sale_details) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not OrderModel.has_required_pairs(sale_details, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        re_prod_fields = {
            "product_name": "--",
            "quantity": "--",
            "product_discount_per": "--",
            "product_discount_desc": "--",
        }

        insert_to_sales_detail = []
        total_price = 0

        # Validate the products field
        if not type(sale_details["products"]) == list:
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        # Validate and process sale discount percentage
        try:
            sale_details["sale_discount_per"] = int(sale_details["sale_discount_per"])
        except:
            return make_response({"ERROR": "INVALID PARAMETERS"}, 401)

        for i in sale_details["products"]:
            # Validate each product's details
            if not OrderModel.has_required_pairs(i, re_prod_fields):
                return make_response({"ERROR": "UNAUTHORIZED"}, 401)

            self.mycursor.execute(
                "SELECT id, price FROM PRODUCTS WHERE NAME = %s", (i["product_name"],)
            )
            if len(result_cursor := self.mycursor.fetchall()) < 1:
                return make_response({"ERROR": "PRODUCT NOT FOUND"}, 404)

            result_cursor = result_cursor[0]
            try:
                i["quantity"] = int(i["quantity"])
                i["product_discount_per"] = int(i["product_discount_per"])
            except:
                return make_response({"ERROR": "INVALID PARAMETERS"}, 401)

            # Prepare sales details for insertion
            insert_to_sales_detail.append(
                [
                    result_cursor["id"],
                    int(i["quantity"]),
                    result_cursor["price"] * i["quantity"],
                    i["product_discount_per"],
                    (i["product_discount_per"] / 100)
                    * (result_cursor["price"] * i["quantity"]),
                    i["product_discount_desc"],
                ]
            )
            total_price += (result_cursor["price"] * i["quantity"]) - (
                i["product_discount_per"] / 100
            ) * (result_cursor["price"] * i["quantity"])

        # Validate and decode the token
        authorization = request.headers.get("authorization")
        try:
            if re.match("^Bearer *([^ ]+) *$", authorization, flags=0) == None:
                return make_response({"ERROR": "INVALID_TOKEN"}, 401)
        except TypeError:
            return make_response({"ERROR": "TOKEN NOT FOUND"}, 400)

        token = authorization.split(" ")[1]
        try:
            tokendata = jwt.decode(token, secret_key, algorithms="HS256")
        except Exception as e:
            return make_response({"ERROR": str(e).upper()}, 401)

        if tokendata["payload"]["token_role"] != "access-token":
            return make_response({"ERROR": "Forbidden"}, 403)

        user_id = tokendata["payload"]["id"]

        # Insert the sale into the database
        try:
            self.mycursor.execute(
                "INSERT INTO SALES (user_id, price, discount_per, discount_price, discount_des) VALUES (%s,%s,%s,%s,%s)",
                (
                    user_id,
                    total_price,
                    sale_details["sale_discount_per"],
                    int((sale_details["sale_discount_per"] / 100) * total_price),
                    sale_details["sale_discount_desc"],
                ),
            )
        except mysql.connector.errors.IntegrityError:
            return make_response({"ERROR": "USER NOT FOUND"}, 404)
        self.db.commit()

        self.mycursor.execute("SELECT last_insert_id()")
        sales_id = self.mycursor.fetchall()[0]["last_insert_id()"]

        # Insert sale details into the database
        for j in insert_to_sales_detail:
            self.mycursor.execute(
                "INSERT INTO SALE_DETAILS (sale_id, product_id, quantity, price, discount_per, discount_price, discount_des) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                (sales_id, j[0], j[1], j[2], j[3], j[4], j[5]),
            )
        self.db.commit()

        return make_response({"MESSAGE": "ORDER HAS BEEN PLACED"}, 201)
