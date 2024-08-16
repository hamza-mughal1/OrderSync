import mysql.connector
from model.config import *


def create_connection():
    """
    Create a connection to the MySQL database using configuration from `db_config`.

    Returns:
        mysql.connector.connection: A connection object to the MySQL database.
    """
    return mysql.connector.connect(
        host=db_config["host"],  # The host of the MySQL database.
        user=db_config["user"],  # The username for MySQL authentication.
        port=db_config["port"],  # The port number where MySQL server is listening.
        password=db_config["password"],  # The password for MySQL authentication.
        database=db_config["database"],  # The name of the database to connect to.
    )
