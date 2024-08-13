import mysql.connector
from model.config import *


def create_connection():
    return mysql.connector.connect(
        host=db_config["host"],
        user=db_config["user"],
        port=db_config["port"],
        password=db_config["password"],
        database=db_config["database"],
    )
