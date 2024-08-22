from model.config import *
from flask import make_response, send_file
from datetime import datetime
import os
from model.mysql_connector_obj import create_connection


class ProductModel:
    def __init__(self):
        """
        Initialize the ProductModel with a database connection and cursor.
        Also sets the page limit for pagination.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)
        self.page_limit = 20

    @staticmethod
    def has_required_pairs(dictionary, required):
        """
        Check if the dictionary contains all required key-value pairs.

        Args:
            dictionary (dict): The dictionary to check.
            required (dict): The required key-value pairs.

        Returns:
            bool: True if all required key-value pairs are present, False otherwise.
        """
        return all(item in dictionary.keys() for item in required.keys())

    def all_products(self, page=0):
        """
        Retrieve all active products with their categories, paginated.

        Args:
            page (int): The page number for pagination. Defaults to 0.

        Returns:
            Response: A JSON response containing the products.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute(
            "SELECT products.id as product_id, products.name as product_name, categories.name as category_name, products.price as product_price  FROM products INNER JOIN categories ON products.category_id = categories.id WHERE products.toggle = 1 and categories.toggle = 1 LIMIT %s OFFSET %s",
            (self.page_limit, self.page_limit * page),
        )
        return make_response({"PRODUCTS": self.mycursor.fetchall()}, 200)

    def add_product(self, product_details):
        """
        Add a new product to the database.

        Args:
            product_details (dict): A dictionary containing 'category_name', 'name', and 'price'.

        Returns:
            Response: A JSON response indicating success or failure.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {
            "category_name": "--",
            "name": "--",
            "price": "--",
        }

        if not type(product_details) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not ProductModel.has_required_pairs(product_details, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        try:
            self.mycursor.execute(
                "INSERT INTO products (category_id, name, price) value ((SELECT id FROM CATEGORIES WHERE NAME = %s),%s,%s)",
                (
                    product_details["category_name"],
                    product_details["name"],
                    product_details["price"],
                ),
            )
        except:
            return make_response(
                {"ERROR": "ERROR WITH THE PARAMETERS OR PRODUCT ALREADY EXISTS"}, 401
            )
        self.db.commit()
        return make_response({"MESSAGE": "PRODUCT HAS BEEN ADDED SUCCESSFULLY"}, 201)

    def delete_product(self, product_details):
        """
        Delete a product from the database.

        Args:
            product_details (dict): A dictionary containing the 'name' of the product to delete.

        Returns:
            Response: A JSON response indicating success or failure.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        re_fields = {"name": "--"}

        if not type(product_details) == dict:
            return make_response(
                {"ERROR": "ONLY JSON DICTIONARY/HASHMAP IS ALLOWED"}, 400
            )

        if not ProductModel.has_required_pairs(product_details, re_fields):
            return make_response({"ERROR": "UNAUTHORIZED"}, 401)

        try:
            self.mycursor.execute(
                "SELECT id FROM products WHERE name = %s", (product_details["name"],)
            )
            id = self.mycursor.fetchall()[0]["id"]
        except:
            return make_response({"ERROR": "PRODUCT NOT FOUND"}, 404)

        try:
            self.mycursor.execute(
                "SELECT sale_id, price, discount_price FROM sale_details where product_id = %s",
                (id,),
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
        return make_response({"MESSAGE": "PRODUCT HAS BEEN DELETED SUCCESSFULLY"}, 201)

    def product_toggle(self, product):
        """
        Toggle the availability of a product (on/off).

        Args:
            product (str): The name of the product to toggle.

        Returns:
            Response: A JSON response indicating success or failure.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute("SELECT * FROM products WHERE name = %s", (product,))
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "PRODUCT NOT FOUND"}, 404)
        self.mycursor.execute(
            "UPDATE products SET toggle = IF(toggle = 1, 0, 1) WHERE name = %s",
            (product,),
        )
        self.db.commit()
        return make_response({"MESSAGE": "PRODUCT TOGGLE UPDATED SUCCESSFULLY"}, 200)

    def product_by_category(self, category):
        """
        Retrieve products by category.

        Args:
            category (str): The name of the category to filter products by.

        Returns:
            Response: A JSON response containing the products in the specified category.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        if category == "None":
            return make_response({"ERROR": "NO CATEGORY WAS PROVIDED"}, 401)

        self.mycursor.execute("SELECT id FROM categories WHERE name = %s", (category,))
        if len(id := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "NO CATEGORY FOUND"}, 404)

        self.mycursor.execute(
            "SELECT name, price FROM products WHERE category_id = %s", (id[0]["id"],)
        )

        return make_response(
            {"Category": category, "products": self.mycursor.fetchall()}, 200
        )

    def product_by_price_range(self, start, range):
        """
        Retrieve products within a specific price range.

        Args:
            start (float): The starting price.
            range (float): The ending price.

        Returns:
            Response: A JSON response containing the products within the specified price range.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute(
            "SELECT name, price FROM products WHERE price > %s and price < %s",
            (start, range),
        )
        return make_response({"products": self.mycursor.fetchall()}, 200)

    def upload_product_image(self, product_name, files):
        """
        Upload or update the image for a specific product.

        Args:
            product_name (str): The name of the product to associate with the image.
            files (dict): The files containing the image to upload.

        Returns:
            Response: A JSON response indicating success or failure.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        allowed_file_ext = ["jpg", "png"]
        file = list(dict(files).values())[0]
        unique_file_name = str(datetime.now().timestamp()).replace(".", "")
        final_unique_name = unique_file_name + file.filename

        if not file.filename.split(".")[-1] in allowed_file_ext:
            return make_response(
                {"ERROR": "FILE TYPE NOT SUPPORTED. (JPG OR PNG)"}, 401
            )

        self.mycursor.execute(
            "SELECT image_path FROM products WHERE name = %s", (product_name,)
        )
        if len(data := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "NO PRODUCT FOUND"}, 404)

        if data[0]["image_path"] == "None":
            self.mycursor.execute(
                "UPDATE products SET image_path = %s WHERE name = %s",
                (final_unique_name, product_name),
            )
            file.save(f"images/{final_unique_name}")
        else:
            try:
                os.remove(f"{data[0]['file_path']}")
            except:
                pass

            self.mycursor.execute(
                "UPDATE products SET image_path = %s WHERE name = %s",
                (final_unique_name, product_name),
            )
            file.save(f"images/{final_unique_name}")

        self.db.commit()
        return make_response({"MESSAGE": "IMAGE HAS BEEN ADDED/UPDATED"}, 201)

    def get_product_image(self, product_name):
        """
        Retrieve the image associated with a specific product.

        Args:
            product_name (str): The name of the product to retrieve the image for.

        Returns:
            Response: The image file or an error message if not found.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute(
            "SELECT image_path FROM products WHERE name = %s", (product_name,)
        )
        if len(data := self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "PRODUCT NOT FOUND"}, 404)

        if os.path.exists(f"images/{data[0]['image_path']}"):
            return send_file(f"images/{data[0]['image_path']}")
        else:
            return make_response({"ERROR": "IMAGE NOT FOUND"}, 404)
