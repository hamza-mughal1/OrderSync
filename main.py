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
        self.mycursor.execute(f"SELECT * FROM PRODUCTS LIMIT {limit} OFFSET {offset}")
        return [list(i) for i in self.mycursor]
    
    def place_order(self, products, quantities):
        insert_to_sales_detail = []
        total_price = 0 
        for pos, i in enumerate(products):
            self.mycursor.execute(f"SELECT ID, PRICE FROM PRODUCTS WHERE NAME = '{i}'")
            result_cursor = list(self.mycursor)[0]
            insert_to_sales_detail.append([result_cursor[0], quantities[pos],result_cursor[1]*quantities[pos]])
            total_price += result_cursor[1]*quantities[pos]

        self.mycursor.execute(f"INSERT INTO SALES (total_amount) value ({total_price})")
        self.db.commit()
        self.mycursor.execute("select last_insert_id()")
        sales_id = list(self.mycursor)[0][0]

        for j in insert_to_sales_detail:
            self.mycursor.execute(f"INSERT INTO SALES_DETAIL (sale_id, product_id, quantity, price) VALUE ({sales_id},{j[0]},{j[1]},{j[2]})")
        
        self.db.commit()

    def all_sales(self):
        sales_list = []
        self.mycursor.execute("SELECT * FROM SALES")
        for i in list(self.mycursor):
            temp_ls = []
            date = i[1]
            price = float(i[2])
            self.mycursor.execute(f"SELECT * FROM SALES_DETAIL WHERE SALE_ID = {i[0]}")
            for j in list(self.mycursor):
                self.mycursor.execute(f"SELECT name, price FROM PRODUCTS WHERE ID = {j[2]}")
                result_cursor = list(self.mycursor)[0]
                temp_ls.append((result_cursor[0],j[3],result_cursor[1],j[4]))

            sales_list.append([temp_ls,date,price])

        return sales_list


mydb = Database(
    host = "localhost",
    user = "root",
    password = "hamza-100",
    database = "ordersync"
    )

# print(mydb.all_products())

# mydb.place_order(["Classic Hot Dog", "Ham Sandwich"],[2, 1])

for i in mydb.all_sales():
    print(i)