import mysql.connector
from model.config import *
from flask import make_response

class OrderModel:
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

    def place_order(self, sale_details):
        re_fields= {
            "user_id" : "--",
            "products": "--",
            "sale_discount_per" : "--",
            "sale_discount_desc": "--"
        }
        
        if not OrderModel.has_required_pairs(sale_details, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        re_prod_fields = {
                "product_name": "--",
                "quantity": "--",
                "product_discount_per": "--",
                "product_discount_desc": "--"
            }
        
        insert_to_sales_detail = []
        total_price = 0 
        if not type(sale_details["products"]) == list:
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)

        for i in sale_details["products"]:
            if not OrderModel.has_required_pairs(i, re_prod_fields):
                return make_response({"ERROR":"UNAUTHORIZED"}, 401)
            
            self.mycursor.execute("SELECT id, price FROM PRODUCTS WHERE NAME = %s",(i['product_name'],))
            if len(result_cursor := self.mycursor.fetchall())<1:
                return make_response({"ERROR":"PRODUCT NOT FOUND"}, 404)
            
            result_cursor = result_cursor[0]

            insert_to_sales_detail.append([
                result_cursor["id"], 
                i["quantity"],
                result_cursor["price"] * i["quantity"],
                i["product_discount_per"],
                (i["product_discount_per"] / 100) * (result_cursor["price"] * i["quantity"]),
                i["product_discount_desc"]
            ])
            total_price += ((result_cursor["price"] * i["quantity"]) - (i["product_discount_per"] / 100) * (result_cursor["price"] * i["quantity"]))

        try:
            self.mycursor.execute("INSERT INTO SALES (user_id, price, discount_per, discount_price, discount_des) VALUES (%s,%s,%s,%s,%s)",(sale_details ['user_id'], total_price, sale_details['sale_discount_per'], int((sale_details ['sale_discount_per'] / 100) * total_price), sale_details ['sale_discount_desc']))
        except mysql.connector.errors.IntegrityError:
            return make_response({"ERROR":"USER NOT FOUND"}, 404)
        self.db.commit()

        self.mycursor.execute("SELECT last_insert_id()")
        sales_id = self.mycursor.fetchall()[0]["last_insert_id()"]

        for j in insert_to_sales_detail:
            self.mycursor.execute("INSERT INTO SALE_DETAILS (sale_id, product_id, quantity, price, discount_per, discount_price, discount_des) VALUES (%s,%s,%s,%s,%s,%s,%s)",(sales_id, j[0], j[1], j[2], j[3], j[4], j[5]))
        self.db.commit()

        return make_response({"MESSAGE":"ORDER HAS BEEN PLACED"},201)

