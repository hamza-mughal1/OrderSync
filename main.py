import json
from pprint import pprint
import mysql.connector
import bcrypt

class Database:
    """
    A class to interact with a MySQL database for handling product, orders, sales, and everything.
    """
    def __init__(self, host, user, password, database):
        """
        Initialize the database connection and cursor.
        """
        self.db = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.mycursor = self.db.cursor()

    @staticmethod
    def generate_hashed_password(password):
        """
        Generate a hashed password with a salt.
        """
        salt = bcrypt.gensalt()
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
        return hashed_password.decode('utf-8')

    def all_products(self, limit=1000, offset=0):
        """
        Retrieve all products from the database with pagination.

        Args:
        - limit (int): Maximum number of products to fetch.
        - offset (int): Offset for pagination.

        Returns:
        - str: JSON-formatted string containing product information.
        """
        products_dic = {}
        self.mycursor.execute(f"SELECT * FROM PRODUCTS LIMIT {limit} OFFSET {offset}")
        result_cursor = list(self.mycursor)

        for pos, result in enumerate(result_cursor):
            products_dic[f"product_{pos+1}"] = {
                "product_id": result[0],
                "category": result[1],
                "product_name": result[2],
                "product_price": result[3]
            }
        
        return 200, products_dic

    def place_order(self, sale):
        """
        Place an order based on the given sale data.

        Args:
        - sale dict.

        structure : 
        sale = {
            "user_id" : --,
            "products": [{
                "product_name": --,
                "quantity": --,
                "product_discount_per": --,
                "product_discount_desc": --
            },
                {
                "product_name": --,
                "quantity": --,
                "product_discount_per": --,
                "product_discount_desc": --
            }],
            "sale_discount_per" : --,
            "sale_discount_desc": --
        }
        

        Returns:
        - None
        """
        insert_to_sales_detail = []
        total_price = 0 

        # Retrieve product details and calculate total price
        for i in sale["products"]:
            self.mycursor.execute(f"SELECT ID, PRICE FROM PRODUCTS WHERE NAME = '{i['product_name']}'")
            result_cursor = list(self.mycursor)[0]
            insert_to_sales_detail.append([
                result_cursor[0], 
                i["quantity"],
                result_cursor[1] * i["quantity"],
                i["product_discount_per"],
                (i["product_discount_per"] / 100) * (result_cursor[1] * i["quantity"]),
                i["product_discount_desc"]
            ])
            total_price += ((result_cursor[1] * i["quantity"]) - (i["product_discount_per"] / 100) * (result_cursor[1] * i["quantity"]))

        # Insert sale information into SALES table
        self.mycursor.execute(f"INSERT INTO SALES (user_id, price, discount_per, discount_price, discount_des) VALUES ({sale['user_id']}, {total_price}, {sale['sale_discount_per']}, {int((sale['sale_discount_per'] / 100) * total_price)}, '{sale['sale_discount_desc']}')")
        self.db.commit()

        # Retrieve the ID of the last inserted sale
        self.mycursor.execute("SELECT last_insert_id()")
        sales_id = list(self.mycursor)[0][0]

        # Insert sale details into SALE_DETAILS table
        for j in insert_to_sales_detail:
            self.mycursor.execute(f"INSERT INTO SALE_DETAILS (sale_id, product_id, quantity, price, discount_per, discount_price, discount_des) VALUES ({sales_id}, {j[0]}, {j[1]}, {j[2]}, {j[3]}, {j[4]}, '{j[5]}')")
        self.db.commit()

    def all_sales(self):
        """
        Retrieve all sales from the database.

        Returns:
        - str: JSON-formatted string containing sale information.
        """
        sales_dic = {}
        self.mycursor.execute("SELECT * FROM SALES")

        for pos, i in enumerate(list(self.mycursor)):
            temp_ls_for_dic = []
            date = i[3]
            price = float(i[2])

            # Retrieve sale details for each sale
            self.mycursor.execute(f"SELECT * FROM SALE_DETAILS WHERE SALE_ID = {i[0]}")
            
            for j in list(self.mycursor):
                self.mycursor.execute(f"SELECT name, price FROM PRODUCTS WHERE ID = {j[2]}")
                result_cursor = list(self.mycursor)[0]
                temp_ls_for_dic.append({
                    "product_name": result_cursor[0],
                    "quantity": j[3],
                    "product_price": result_cursor[1],
                    "total_price": j[4],
                    "discount_percentage": j[5],
                    "discount_price": j[6],
                    "discount_description": j[7]
                })

            # Build dictionary for each sale
            sales_dic[f"sale_{pos+1}"] = {
                "products": temp_ls_for_dic,
                "date": date.isoformat(),
                "price": price,
                "sale_discount_percentage": i[4],
                "sale_discount_price": i[5],
                "sale_discount_description": i[6]
            }

        return 200, sales_dic

    def product_add(self, product_info, add_by_cateogry_id = False):
        """
        product = {
                "category_id": --, OR "category_name": --,
                "name": --,
                "price": --,
        }
        
        
        """
        product_info = json.loads(product_info)
        if add_by_cateogry_id:
            self.mycursor.execute(f"INSERT INTO products (category_id, name, price) value ({product_info["category_id"]}, {product_info ["name"]}, {product_info["price"]})")
        else:
            self.mycursor.execute(f"INSERT INTO products (category_id, name, price) value ((SELECT id FROM CATEGORY WHERE NAME = {product_info["category_name"]}), {product_info ["name"]}, {product_info["price"]})")

        self.db.commit()
        return 201, "Product added successfully"
            
    def product_delete(self, product_details):
        product_id = json.loads(product_details)["product_id"]

        self.mycursor.execute(f"SELECT sale_id, price, discount_price FROM sale_details where product_id = {product_id}")
        update_sales = [(i[0],i[1]-i[2]) for i in list(self.mycursor)]
        self.mycursor.execute(f"DELETE FROM sale_details WHERE product_id = {product_id}")
        for i in update_sales:
            self.mycursor.execute(f"UPDATE sales SET price = price - {i[1]} where id = {i[0]}")
            self.db.commit()
            self.mycursor.execute(f"SELECT price from sales where id = {i[0]}")
            price = list(self.mycursor)[0][0]
            self.mycursor.execute(f"SELECT discount_per FROM sales WHERE id = {i[0]}")
            discount_per = list(self.mycursor)[0][0]
            discount_price = price*(discount_per/100)
            self.mycursor.execute(f"UPDATE sales SET discount_price = {discount_price} where id = {i[0]}")
            self.db.commit()

        self.mycursor.execute(f"DELETE FROM products WHERE id = {product_id}")
        self.db.commit()
               
    def product_update_name(self, product_details, update_by_id = False):
        """
        product_details = {
                "product_id": --, or "product_old_name": --,
                "new_name": --
        }
        """
        product_details = json.loads(product_details)
        if update_by_id:
            self.mycursor.execute(f"UPDATE FROM products SET name = {product_details["new_name"]} where id = {product_details["product_id"]}")     
        else:
            self.mycursor.execute(f"UPDATE FROM products SET name = {product_details["new_name"]} where name = {product_details["product_old_name"]}")

        self.db.commit() 

    def product_update_price(self, product_details, update_by_id = False):
        """
        product_details = {
                "product_id": --, or "product_name": --,
                "new_price": --
        }
        """
        product_details = json.loads(product_details)
        if update_by_id:
            self.mycursor.execute(f"UPDATE FROM products SET price = {product_details["new_price"]} where id = {product_details["product_id"]}")     
        else:
            self.mycursor.execute(f"UPDATE FROM products SET price = {product_details["new_price"]} where name = {product_details["product_name"]}") 

    def user_create(self, user_details):
        """
        user_details = {
            "name": --,
            "user_name": --,
            "password": --,        
        }
        """
        try:
            user_details = json.loads(user_details)
        except AttributeError:
            return 400, "Bad request (Incorrect parameters)" 
        try:
            hashed_pass = Database.generate_hashed_password(open("salt.txt").readline(), user_details["password"])
        except (KeyError, TypeError):
            return 400, "Bad request (Incomplete parameters)"
        except:
            return 500, "Internal server error"
           
        try:
            self.mycursor.execute(f"INSERT INTO users (name, user_name, password) value ('{user_details["name"]}', '{user_details["user_name"]}', '{hashed_pass}')")
            self.db.commit()
            return 201, "User registered successfully"
        except mysql.connector.errors.IntegrityError:
            return 409, "Username already exists"             
    
    def verify_user(self, user_details):
        """
        user_details = {
            "user_name": --,
            "password": --,        
        }
        """
        try:
            user_details = json.loads(user_details)
            self.mycursor.execute(f"SELECT password FROM users WHERE user_name = '{user_details["user_name"]}'")
            if bcrypt.checkpw(user_details["password"].encode("utf-8"), list(self.mycursor)[0][0].encode("utf-8")):
                return 200, "Successfully logged in!"
            else:
                return 401, "Wrong credentials!"
        except KeyError:
            return 400, "Bad request (incomplete parameters)"
        except IndexError:
            return 401, "Wrong credentials!"
        except:
            return 400, "Bad request"

if __name__ == "__main__":
    # Initialize Database instance
    mydb = Database(
        host="localhost",
        user="root",
        password="hamza-100",
        database="ordersync"
    )


    print(mydb.all_products()[1])

    # Print all sales data
    # pprint(json.loads(mydb.all_sales()), sort_dicts=False)
    # mydb.product_delete(json.dumps(
    #     {"product_id": 4}
    #     ))

    # Example of placing an order (commented out)
    # sale = {
    #     "user_id": 1,
    #     "products": [{
    #         "product_name": "Cookies",
    #         "quantity": 5,
    #         "product_discount_per": 0,
    #         "product_discount_desc": "None"
    #     },
    #     {
    #         "product_name": "Vanilla Ice Cream",
    #         "quantity": 3,
    #         "product_discount_per": 0,
    #         "product_discount_desc": "None"
    #     }],
    #     "sale_discount_per": 0,
    #     "sale_discount_desc": "None"
    # }

    # mydb.place_order(json.dumps(sale))


    # print(mydb.verify_user(json.dumps({
    #         "user_name": input(),
    # })))

    # print(mydb.user_create(
    #     json.dumps({
    #     "name": "Azan",
    #     "user_name": "AzanMughal",
    #     "password": "azan100"
    # })))

