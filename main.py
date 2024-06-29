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

    def all_products(self):
        self.mycursor.execute("select * from products")
        return [list(i) for i in self.mycursor]
    
    def place_order(self, products, quantities):
        insert_to_sales_detail = []
        total_price = 0 
        for pos, i in enumerate(products):
            self.mycursor.execute(f"SELECT ID, PRICE FROM PRODUCTS WHERE NAME = '{i}'")
            ResultCursor = list(self.mycursor)[0]
            insert_to_sales_detail.append([ResultCursor[0], quantities[pos],ResultCursor[1]*quantities[pos]])
            total_price += ResultCursor[1]*quantities[pos]

        self.mycursor.execute(f"INSERT INTO SALES (total_amount) value ({total_price})")
        self.db.commit()
        self.mycursor.execute("select last_insert_id()")
        sales_id = list(self.mycursor)[0][0]

        for j in insert_to_sales_detail:
            self.mycursor.execute(f"INSERT INTO SALES_DETAIL (sale_id, product_id, quantity, price) VALUE ({sales_id},{j[0]},{j[1]},{j[2]})")
        
        self.db.commit()



mydb = Database(
    host = "localhost",
    user = "root",
    password = "hamza-100",
    database = "ordersync"
    )

# print(mydb.all_products())

mydb.place_order(["Margherita pizza large"],[5])