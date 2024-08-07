import mysql.connector
from model.config import *
from flask import make_response

class CategoryModel:
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


    def category_toggle(self, category):
        self.mycursor.execute("SELECT * FROM categories WHERE name = %s", (category,))
        if len(self.mycursor.fetchall())<1:
            return make_response({"ERROR":"CATEGORY NOT FOUND"}, 404)
        self.mycursor.execute("UPDATE categories SET toggle = IF(toggle = 1, 0, 1) WHERE name = %s", (category,))
        self.db.commit()
        return make_response({"MESSAGE":"CATEGORY TOGGLE HAS UPDATED SUCCESSFULLY"}, 200)
