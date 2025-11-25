# data/db_connection.py

import mysql.connector
from mysql.connector import Error
from config.settings import DB_CONFIG

class DatabaseConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        """Establishes connection to MySQL database."""
        try:
            self.connection = mysql.connector.connect(
                host=DB_CONFIG["host"],
                user=DB_CONFIG["user"],
                password=DB_CONFIG["password"],
                database=DB_CONFIG["database"],
                port=DB_CONFIG.get("port", 3306)
            )
            if self.connection.is_connected():
                print("✅ Connected to MySQL database")
            return self.connection
        except Error as e:
            print(f"❌ Error connecting to MySQL: {e}")
            return None

    def get_cursor(self):
        """Returns a cursor object for executing queries."""
        if self.connection and self.connection.is_connected():
            return self.connection.cursor(dictionary=True)
        else:
            raise Exception("Database connection is not established.")

    def close(self):
        """Closes the database connection."""
        if self.connection and self.connection.is_connected():
            self.connection.close()
            print("✅ MySQL connection closed")
