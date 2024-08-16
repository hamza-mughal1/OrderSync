from model.config import *
from flask import make_response
from model.mysql_connector_obj import create_connection

class SaleModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

    @staticmethod
    def month_name_by_number(month_no):
        """
        Converts a given month number to its corresponding month name.

        Args:
            month_no (int or str): The month number (1 for January, 2 for February, etc.).

        Returns:
            str: The name of the corresponding month.
        """
        months = [
                    "January", "February", "March", "April", "May", "June",
                    "July", "August", "September", "October", "November", "December"
                ]

        return months[int(month_no)-1]

    @staticmethod
    def growth_percentage_calculator(lis):
        """
        Calculates the percentage growth in sales prices between consecutive months.

        Args:
            lis (list): A list of dictionaries, each containing 'month' and 'price' keys.
                        The 'month' key should be an integer representing the month number,
                        and the 'price' key should be an integer representing the sales price.

        Returns:
            dict: A dictionary where each key is a string representing the range of months
                (e.g., "January - February"), and each value is the percentage growth
                between those months as a string (e.g., "10.00%"). If the previous sale price is 0,
                the value will be "previous sale was 0".
        """
        pre = None
        final_dict = {}
        for i in lis:
            if pre == None:
                pre = i
            else:
                if pre["price"] == 0:
                    final_dict[f"{SaleModel.month_name_by_number(pre["month"])} - {SaleModel.month_name_by_number(i["month"])}"] = "previous sale was 0"
                else:
                    final_dict[f"{SaleModel.month_name_by_number(pre["month"])} - {SaleModel.month_name_by_number(i["month"])}"] = f"{round(((int(i["price"]) - int(pre["price"]))/int(pre["price"]))*100,2)}%"
                pre = i

        return final_dict

    def all_sales(self):
        """
        Calculate all sales and formate it into a nice dict
        
        Returns:
            dict: A dictionary containing all the sales
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
        """
        Perform calculations and analysis on the sales and generate sale revenue report

        Returns:
            Dict/JSON: A dictionary containing sales revenue report by day, week, month, and year period.
        """
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
        """
        Calculate and analysis of products and generate report of top three most selling products.
        Returns:
                Dict/JSON: A dictionary containing report of most selling three products by day, week, month, and year period.
        
        """
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
        """
        Calculate and perform analysis on sales and generate report of two most selling days by week, month, and year period.
        Return:
                Dict/JSON: A dictionary containing the report of two most selling days.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
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
        """
        Calculate and perform analysis on sales and generate report of three most selling hours (peak hours) by week, month, and year period.
        Return:
                Dict/JSON: A dictionary containing the report of peak hours.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
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

    def delta_percentage_by_months(self):
        """
        Calculate and perform analysis on sales and generate report of three most selling hours (peak hours) by week, month, and year period.
        Return:
                Dict/JSON: A dictionary containing the report of peak hours.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        self.mycursor.execute("SELECT MONTH(DATE) as month, SUM(price) as price FROM SALES GROUP BY MONTH(DATE)")
        sales_delta = SaleModel.growth_percentage_calculator(sorted(self.mycursor.fetchall(),key=lambda x : x["month"]))

        print(sales_delta)

        return make_response({"SALES PERCENTAGE DELTA":sales_delta}, 200)
