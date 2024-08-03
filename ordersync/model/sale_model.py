from calendar import month
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
        sales_dic = []
        self.mycursor.execute("SELECT * FROM SALES")

        for i in self.mycursor.fetchall():
            temp_ls_for_dic = []
            date = i["date"]
            price = float(i["price"])

            self.mycursor.execute(
                "SELECT * FROM SALE_DETAILS WHERE SALE_ID = %s", (i["id"],)
            )

            for j in self.mycursor.fetchall():

                self.mycursor.execute(
                    "SELECT name, price FROM PRODUCTS WHERE ID = %s", (j["product_id"],)
                )
                result_cursor = self.mycursor.fetchall()[0]

                temp_ls_for_dic.append(
                    {
                        "product_name": result_cursor["name"],
                        "quantity": j["quantity"],
                        "product_price": result_cursor["price"],
                        "total_price": j["price"],
                        "discount_percentage": j["discount_per"],
                        "discount_price": j["discount_price"],
                        "discount_description": j["discount_des"],
                    }
                )

            sales_dic.append(
                {
                    "products": temp_ls_for_dic,
                    "date": date.isoformat(),
                    "price": price,
                    "sale_discount_percentage": i["discount_per"],
                    "sale_discount_price": i["discount_price"],
                    "sale_discount_description": i["discount_des"],
                }
            )

        return make_response({"SALES": sales_dic}, 200)

    def sales_revenue(self):
        try:
            self.mycursor.execute(
                "SELECT SUM(price) AS revenue FROM sales WHERE DATE(sales.date) = CURDATE()"
            )
            this_day = int(self.mycursor.fetchall()[0]["revenue"])
            self.mycursor.execute(
                "SELECT sum(price) as revenue FROM sales WHERE WEEK(sales.date) = WEEK(CURDATE()) AND MONTH(sales.date) = MONTH(CURDATE()) AND YEAR(sales.date) = YEAR(CURDATE())"
            )
            this_week = int(self.mycursor.fetchall()[0]["revenue"])
            self.mycursor.execute(
                "SELECT sum(price) as revenue FROM sales WHERE MONTH(sales.date) = MONTH(CURDATE()) AND YEAR(sales.date) = YEAR(CURDATE())"
            )
            this_month = int(self.mycursor.fetchall()[0]["revenue"])
            self.mycursor.execute(
                "SELECT sum(price) as revenue FROM sales WHERE YEAR(sales.date) = YEAR(CURDATE())"
            )
            this_year = int(self.mycursor.fetchall()[0]["revenue"])

            return make_response(
                {
                    "THIS DAY REVENUE": this_day,
                    "THIS WEEK REVENUE": this_week,
                    "THIS MONTH REVENUE": this_month,
                    "THIS YEAR REVENUE": this_year,
                },
                200,
            )
        except:
            return make_response({"ERROR":"INTERNAL SERVER ERROR"}, 500)
