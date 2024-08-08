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

    def top_three_products(self):
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute("""SELECT 
                                products.name, 
                                sales_data.total_quantity
                            FROM 
                                (
                                    SELECT 
                                        sale_details.product_id, 
                                        SUM(sale_details.quantity) AS total_quantity
                                    FROM 
                                        sale_details
                                    INNER JOIN 
                                        (
                                            SELECT 
                                                id 
                                            FROM 
                                                sales 
                                            WHERE 
                                                DATE(date) = CURDATE()
                                        ) AS filtered_sales 
                                    ON 
                                        sale_details.sale_id = filtered_sales.id
                                    GROUP BY 
                                        sale_details.product_id
                                ) AS sales_data
                            INNER JOIN 
                                products 
                            ON 
                                sales_data.product_id = products.id
                            ORDER BY 
                                sales_data.total_quantity DESC
                            LIMIT 3;""")
        today = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                products.name, 
                                sales_data.total_quantity
                            FROM 
                                (
                                    SELECT 
                                        sale_details.product_id, 
                                        SUM(sale_details.quantity) AS total_quantity
                                    FROM 
                                        sale_details
                                    INNER JOIN 
                                        (
                                            SELECT 
                                                id 
                                            FROM 
                                                sales 
                                            WHERE 
                                                WEEK(date) = WEEK(CURDATE()) 
                                                AND MONTH(date) = MONTH(CURDATE())
                                                AND YEAR(date) = YEAR(CURDATE())
                                        ) AS filtered_sales 
                                    ON 
                                        sale_details.sale_id = filtered_sales.id
                                    GROUP BY 
                                        sale_details.product_id
                                ) AS sales_data
                            INNER JOIN 
                                products 
                            ON 
                                sales_data.product_id = products.id
                            ORDER BY 
                                sales_data.total_quantity DESC
                            LIMIT 3;""")
        week = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                products.name, 
                                sales_data.total_quantity
                            FROM 
                                (
                                    SELECT 
                                        sale_details.product_id, 
                                        SUM(sale_details.quantity) AS total_quantity
                                    FROM 
                                        sale_details
                                    INNER JOIN 
                                        (
                                            SELECT 
                                                id 
                                            FROM 
                                                sales 
                                            WHERE 
                                                MONTH(date) = MONTH(CURDATE())
                                                AND YEAR(date) = YEAR(CURDATE())
                                        ) AS filtered_sales 
                                    ON 
                                        sale_details.sale_id = filtered_sales.id
                                    GROUP BY 
                                        sale_details.product_id
                                ) AS sales_data
                            INNER JOIN 
                                products 
                            ON 
                                sales_data.product_id = products.id
                            ORDER BY 
                                sales_data.total_quantity DESC
                            LIMIT 3;""")
        month = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                products.name, 
                                sales_data.total_quantity
                            FROM 
                                (
                                    SELECT 
                                        sale_details.product_id, 
                                        SUM(sale_details.quantity) AS total_quantity
                                    FROM 
                                        sale_details
                                    INNER JOIN 
                                        (
                                            SELECT 
                                                id 
                                            FROM 
                                                sales 
                                            WHERE 
                                                YEAR(date) = YEAR(CURDATE())
                                        ) AS filtered_sales 
                                    ON 
                                        sale_details.sale_id = filtered_sales.id
                                    GROUP BY 
                                        sale_details.product_id
                                ) AS sales_data
                            INNER JOIN 
                                products 
                            ON 
                                sales_data.product_id = products.id
                            ORDER BY 
                                sales_data.total_quantity DESC
                            LIMIT 3;""")
        year = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                products.name, 
                                sales_data.total_quantity
                            FROM 
                                (
                                    SELECT 
                                        sale_details.product_id, 
                                        SUM(sale_details.quantity) AS total_quantity
                                    FROM 
                                        sale_details
                                    INNER JOIN 
                                        (
                                            SELECT 
                                                id 
                                            FROM 
                                                sales 
                                        ) AS filtered_sales 
                                    ON 
                                        sale_details.sale_id = filtered_sales.id
                                    GROUP BY 
                                        sale_details.product_id
                                ) AS sales_data
                            INNER JOIN 
                                products 
                            ON 
                                sales_data.product_id = products.id
                            ORDER BY 
                                sales_data.total_quantity DESC
                            LIMIT 3;""")
        all_time = self.mycursor.fetchall()

        dic = {"TODAY":today,
               "WEEK":week,
               "MONTH":month,
               "YEAR":year,
               "ALL TIME":all_time}
        
        return make_response({"REPORT":dic}, 200)
    
    def top_two_selling_days(self):
        self.mycursor.execute("""SELECT 
	                                DATE(date) AS sale_date, SUM(price) AS total_price
                                FROM 
                                    sales WHERE WEEK(date) = WEEK(CURDATE())
                                    AND MONTH(date) = MONTH(CURDATE())
                                    AND YEAR(date) = YEAR(CURDATE())   
                                GROUP BY 
	                                DATE(date) 
                                    ORDER BY total_price DESC
                                LIMIT 2;""")
        week = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
	                                DATE(date) AS sale_date, SUM(price) AS total_price
                                FROM sales
                                    WHERE
                                        MONTH(date) = MONTH(CURDATE())
                                        AND YEAR(date) = YEAR(CURDATE())    
                                GROUP BY 
	                                DATE(date) 
                                    ORDER BY total_price DESC
                                LIMIT 2;""")
        month = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
	                                DATE(date) AS sale_date, SUM(price) AS total_price
                                FROM sales
                                    WHERE 
                                        YEAR(date) = YEAR(CURDATE())    
                                GROUP BY 
	                                DATE(date) 
                                    ORDER BY total_price DESC
                                LIMIT 2;""")
        year = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
	                                DATE(date) AS sale_date, SUM(price) AS total_price
                                FROM sales
                                    GROUP BY 
	                                    DATE(date) 
                                        ORDER BY total_price DESC
                                LIMIT 2;""")
        all_time = self.mycursor.fetchall()

        dic = {"WEEK":week,
               "MONTH":month,
               "YEAR":year,
               "ALL_TIME":all_time}
        
        return make_response({"REPORT":dic}, 200)
    
    def most_selling_hours(self):
        self.mycursor.execute("""SELECT 
                                IF(HOUR>12,CONCAT(IF(MOD(HOUR,12)=0,12,MOD(HOUR,12)), "pm"),CONCAT(HOUR,"am")) as hour, total_price
                                FROM (SELECT 
                                    HOUR(date) as HOUR, SUM(price) as total_price
                                FROM 
                                    sales
                                    WHERE DATE(date) = CURDATE()
                                GROUP BY 
                                    HOUR(date) 
                                ORDER BY total_price DESC
                                LIMIT 3) as sales;""")
        today = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                IF(HOUR>12,CONCAT(IF(MOD(HOUR,12)=0,12,MOD(HOUR,12)), "pm"),CONCAT(HOUR,"am")) as hour, total_price
                                FROM (SELECT 
                                    HOUR(date) as HOUR, SUM(price) as total_price
                                FROM 
                                    sales
                                    WHERE WEEK(date) = WEEK(CURDATE())
                                    AND MONTH(date) = MONTH(CURDATE())
                                    AND YEAR(date) = YEAR(CURDATE())
                                GROUP BY 
                                    HOUR(date) 
                                ORDER BY total_price DESC
                                LIMIT 3) as sales;""")
        week = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                IF(HOUR>12,CONCAT(IF(MOD(HOUR,12)=0,12,MOD(HOUR,12)), "pm"),CONCAT(HOUR,"am")) as hour, total_price
                                FROM (SELECT 
                                    HOUR(date) as HOUR, SUM(price) as total_price
                                FROM 
                                    sales
                                    WHERE MONTH(date) = MONTH(CURDATE())
                                    AND YEAR(date) = YEAR(CURDATE())
                                GROUP BY 
                                    HOUR(date) 
                                ORDER BY total_price DESC
                                LIMIT 3) as sales;""")
        month = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                IF(HOUR>12,CONCAT(IF(MOD(HOUR,12)=0,12,MOD(HOUR,12)), "pm"),CONCAT(HOUR,"am")) as hour, total_price
                                FROM (SELECT 
                                    HOUR(date) as HOUR, SUM(price) as total_price
                                FROM 
                                    sales
                                    WHERE YEAR(date) = YEAR(CURDATE())
                                GROUP BY 
                                    HOUR(date) 
                                ORDER BY total_price DESC
                                LIMIT 3) as sales;""")
        year = self.mycursor.fetchall()
        self.mycursor.execute("""SELECT 
                                IF(HOUR>12,CONCAT(IF(MOD(HOUR,12)=0,12,MOD(HOUR,12)), "pm"),CONCAT(HOUR,"am")) as hour, total_price
                                FROM (SELECT 
                                    HOUR(date) as HOUR, SUM(price) as total_price
                                FROM 
                                    sales
                                GROUP BY 
                                    HOUR(date) 
                                ORDER BY total_price DESC
                                LIMIT 3) as sales;""")
        all_time = self.mycursor.fetchall()

        dic = { "TODAY":today,
                "WEEK":week,
                "MONTH":month,
                "YEAR":year,
                "ALL_TIME":all_time}
        
        return make_response({"REPORT":dic}, 200)
