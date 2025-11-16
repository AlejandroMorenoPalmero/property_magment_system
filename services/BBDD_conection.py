"""
Connection to the MySQL database using environment variables.
"""


from dotenv import load_dotenv
import os
import mysql.connector

load_dotenv()


def get_connection():
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT", "3306")),
            autocommit=True,  # opcional
        )
        conn.ping(reconnect=True, attempts=3, delay=2)
        print("Database connection established.")
        return conn
        
    except mysql.connector.Error as e:
        raise RuntimeError(f"Error de conexión MySQL: {e}")