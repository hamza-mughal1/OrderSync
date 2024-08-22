from model.config import *
from flask import make_response
from model.mysql_connector_obj import create_connection


class CategoryModel:
    def __init__(self):
        """
        Initialize the database connection and cursor.
        """
        self.db = create_connection()
        self.mycursor = self.db.cursor(dictionary=True)

    def category_toggle(self, category):
        """
        Toggle the 'toggle' status of a category in the database.

        Args:
            category (str): The name of the category to be toggled.

        Returns:
            Response: A Flask response object with a message and HTTP status code.
        """
        self.mycursor.close()
        self.db.reconnect()
        self.mycursor = self.db.cursor(dictionary=True)
        # Check if the category exists in the database
        self.mycursor.execute("SELECT * FROM categories WHERE name = %s", (category,))
        if len(self.mycursor.fetchall()) < 1:
            return make_response({"ERROR": "CATEGORY NOT FOUND"}, 404)

        # Toggle the 'toggle' status of the category
        self.mycursor.execute(
            "UPDATE categories SET toggle = IF(toggle = 1, 0, 1) WHERE name = %s",
            (category,),
        )
        self.db.commit()
        return make_response(
            {"MESSAGE": "CATEGORY TOGGLE HAS UPDATED SUCCESSFULLY"}, 200
        )
