import json
from pprint import pprint

import mysql.connector


class Database:
    def __init__(self, host, user, password, database):
        self.db = mysql.connector.connect(
            host = host,
            user = user,
            password = password,
            database = database
            ) 

        self.mycursor = self.db.cursor()

    def all_products(self, limit = 1000, offset = 0):
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
                

        return json.dumps(products_dic)


    def place_order(self, sale):
        sale = json.loads(sale)
        """
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
        
        """
        insert_to_sales_detail = []
        total_price = 0 

        for i in sale["products"]:
            self.mycursor.execute(f"SELECT ID, PRICE FROM PRODUCTS WHERE NAME = '{i["product_name"]}'")
            result_cursor = list(self.mycursor)[0]
            insert_to_sales_detail.append([result_cursor[0], i["quantity"],result_cursor[1]*i["quantity"], i["product_discount_per"], (i["product_discount_per"]/100)*(result_cursor[1]*i["quantity"]), i["product_discount_desc"]])
            total_price += result_cursor[1]*i["quantity"]

        self.mycursor.execute(f"INSERT INTO SALES (user_id, price, discount_per, discount_price,  discount_des) value ({sale["user_id"]},{total_price},{sale["sale_discount_per"]},{int((sale["sale_discount_per"]/100)*total_price)},'{sale["sale_discount_desc"]}')")
        
        self.db.commit()
        self.mycursor.execute("select last_insert_id()")
        sales_id = list(self.mycursor)[0][0]

        for j in insert_to_sales_detail:
            self.mycursor.execute(f"INSERT INTO SALE_DETAILS (sale_id, product_id, quantity, price, discount_per, discount_price,  discount_des) VALUE ({sales_id},{j[0]},{j[1]},{j[2]}, {j[3]}, {j[4]}, '{j[5]}')")
        
        self.db.commit()

    def all_sales(self):
        sales_dic = {}
        self.mycursor.execute("SELECT * FROM SALES")
        for pos, i in enumerate(list(self.mycursor)):
            temp_ls_for_dic = []
            date = i[3]
            price = float(i[2])
            self.mycursor.execute(f"SELECT * FROM SALE_DETAILS WHERE SALE_ID = {i[0]}")
            for j in list(self.mycursor):
                self.mycursor.execute(f"SELECT name, price FROM PRODUCTS WHERE ID = {j[2]}")
                result_cursor = list(self.mycursor)[0]
                temp_ls_for_dic.append(

                        {"product_name": result_cursor[0],
                         "quantity": j[3],
                         "product_price": result_cursor[1],
                         "total_price": j[4],
                         "discount_percentage": j[5],
                         "discount_price": j[6],
                         "discount_description": j[7]}

                )


            sales_dic[f"sale_{pos+1}"] = {
                "products": temp_ls_for_dic,
                "date": date.isoformat(),
                "price": price,
                "sale_discount_percentage": i[4],
                "sale_discount_price": i[5],
                "sale_discount_description": i[6]
            }

        return json.dumps(sales_dic)

if __name__ == "__main__":
    mydb = Database(
        host = "localhost",
        user = "root",
        password = "hamza-100",
        database = "ordersync"
        )


    pprint(json.loads(mydb.all_sales()), sort_dicts=False)

    # pprint(json.loads(mydb.all_products()))


    # sale = {
    #     "user_id":1,
    #     "products": [{
    #         "product_name": "Coffee",
    #         "quantity": 2,
    #         "product_discount_per": 10,
    #         "product_discount_desc": r"10% off for regular customers"
    #         },
    #         {
    #         "product_name": "Chocolate Ice Cream",
    #         "quantity": 3,
    #         "product_discount_per": 0,
    #         "product_discount_desc": "None"
    #         }],
    #     "sale_discount_per" : 0,
    #     "sale_discount_desc": "None"
    # }

    # mydb.place_order(sale)