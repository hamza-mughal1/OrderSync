import mysql.connector
from model.config import *
from flask import make_response

class ProductModel:
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

        self.page_limit = 20

    @staticmethod
    def has_required_pairs(dictionary, required):
        return all(item in dictionary.keys() for item in required.keys())

    def all_products(self, page=0):
        self.mycursor.execute("SELECT products.id as product_id, products.name as product_name, categories.name as category_name, products.price as product_price  FROM products INNER JOIN categories ON products.category_id = categories.id WHERE products.toggle = 1 and categories.toggle = 1 LIMIT %s OFFSET %s", (self.page_limit, self.page_limit*page))
        return make_response({"PRODUCTS" : self.mycursor.fetchall()}, 200)

    def add_product(self, product_details):
        re_fields = {
                "category_name": "--",
                "name": "--",
                "price": "--",
        }

        if not type(product_details) == dict:
            return make_response({"ERROR":"ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400)
        
        if not ProductModel.has_required_pairs(product_details, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        try:
            self.mycursor.execute("INSERT INTO products (category_id, name, price) value ((SELECT id FROM CATEGORIES WHERE NAME = %s),%s,%s)",(product_details["category_name"], product_details["name"],product_details["price"]))
        except:
            return make_response({"ERROR":"ERROR WITH THE PARAMETERS OR PRODUCT ALREADY EXISTS"}, 401)
        self.db.commit()
        return make_response({"MESSAGE":"PRODUCT HAS BEEN ADDED SUCCESSFULLY"}, 201) 

    def delete_product(self, product_details):
        re_fields = {
            "name" : "--"
        }

        if not type(product_details) == dict:
            return make_response({"ERROR":"ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400)

        if not ProductModel.has_required_pairs(product_details, re_fields):
            return make_response({"ERROR":"UNAUTHORIZED"}, 401)
        
        try:
            self.mycursor.execute("SELECT id FROM products WHERE name = %s",(product_details["name"],))
            id = self.mycursor.fetchall()[0]["id"]
        except:
            return make_response({"ERROR":"PRODUCT NOT FOUND"}, 404)
        
        try:
            self.mycursor.execute("SELECT sale_id, price, discount_price FROM sale_details where product_id = %s",(id,))
            result = self.mycursor.fetchall()
            self.mycursor.execute("DELETE FROM sale_details WHERE product_id = %s", (id,))
            for i in result:
                self.mycursor.execute("UPDATE sales SET price = price - %s where id = %s", (i["price"], i["sale_id"]))
                self.db.commit()
                self.mycursor.execute("SELECT price, discount from sales where id = %s", (i[0],))
                price = self.mycursor.fetchall()[0]["price"]
                discount_per = self.mycursor.fetchall()[0]["discount"]
                discount_price = price*(discount_per/100)
                self.mycursor.execute("UPDATE sales SET discount_price = %s where id = %s",(discount_price, i[0]))
                self.db.commit()
        except:
            return make_response({"ERROR":"INTERNAL SERVER ERROR"}, 500)
        self.mycursor.execute("DELETE FROM products WHERE id = %s",(id,))
        self.db.commit()
        return make_response({"MESSAGE":"PRODUCT HAS BEEN DELETED SUCCESSFULLY"}, 201)         

    def product_toggle(self, product):
        self.mycursor.execute("SELECT * FROM products WHERE name = %s", (product,))
        if len(self.mycursor.fetchall())<1:
            return make_response({"ERROR":"PRODUCT NOT FOUND"}, 404)
        self.mycursor.execute("UPDATE products SET toggle = IF(toggle = 1, 0, 1) WHERE name = %s", (product,))
        self.db.commit()
        return make_response({"MESSAGE":"PRODUCT TOGGLE UPDATED SUCCESSFULLY"}, 200)

    def product_by_category(self, category):
        if category == "None":
            return make_response({"ERROR":"NO CATEGORY WAS PROVIDED"}, 401)
        
        self.mycursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        if len(id := self.mycursor.fetchall())<1:
            return make_response({"ERROR":"NO CATEGORY FOUND"}, 404)
        
        self.mycursor.execute("SELECT name, price FROM products WHERE category_id = %s", (id[0]["id"],))

        return make_response({"Category":category, "products":self.mycursor.fetchall()}, 200)
    
    def product_by_price_range(self, start, range):
        self.mycursor.execute("SELECT name, price FROM products WHERE price > %s and price < %s",(start, range))
        return make_response({"products":self.mycursor.fetchall()}, 200)
    
