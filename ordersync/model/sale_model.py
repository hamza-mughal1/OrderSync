import mysql.connector
from model.config import *
from flask import make_response

class SaleModel:
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


    def all_sales(self):
        """
        Retrieve all sales from the database.

        Returns:
        - str: JSON-formatted string containing sale information.
        """
        sales_dic = {}
        self.mycursor.execute("SELECT * FROM SALES")

        for pos, i in enumerate(self.mycursor.fetchall()):
            temp_ls_for_dic = []
            date = i["date"]
            price = float(i["price"])

            # Retrieve sale details for each sale
            self.mycursor.execute("SELECT * FROM SALE_DETAILS WHERE SALE_ID = %s",(i["id"],))
            
            for j in self.mycursor.fetchall():
                
                self.mycursor.execute("SELECT name, price FROM PRODUCTS WHERE ID = %s",(j["product_id"],))
                result_cursor = self.mycursor.fetchall()[0]

                temp_ls_for_dic.append({
                    "product_name": result_cursor["name"],
                    "quantity": j["quantity"],
                    "product_price": result_cursor["price"],
                    "total_price": j["price"],
                    "discount_percentage": j["discount_per"],
                    "discount_price": j["discount_price"],
                    "discount_description": j["discount_des"]
                })

            # Build dictionary for each sale
            sales_dic[f"sale_{pos+1}"] = {
                "products": temp_ls_for_dic,
                "date": date.isoformat(),
                "price": price,
                "sale_discount_percentage": i["discount_per"],
                "sale_discount_price": i["discount_price"],
                "sale_discount_description": i["discount_des"]
            }

        return make_response(sales_dic, 200)
