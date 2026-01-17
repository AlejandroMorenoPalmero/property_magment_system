"""
Shared database utilities for backward compatibility.
Provides simple database access functions for frontend.
"""

from dotenv import load_dotenv
import os
import mysql.connector
from mysql.connector import Error
from typing import List, Tuple

load_dotenv()


def get_connection() -> mysql.connector.MySQLConnection:
    """
    Get database connection using environment variables.
    
    Returns:
        mysql.connector.MySQLConnection: Active database connection
        
    Raises:
        RuntimeError: If connection fails
    """
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST") or os.getenv("MYSQL_HOST"),
            user=os.getenv("DB_USER") or os.getenv("MYSQL_USER"),
            password=os.getenv("DB_PASS") or os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("DB_NAME") or os.getenv("MYSQL_DATABASE"),
            port=int(os.getenv("DB_PORT") or os.getenv("MYSQL_PORT", "3306")),
            autocommit=True,
        )
        connection.ping(reconnect=True, attempts=3, delay=2)
        return connection
    except Error as e:
        raise RuntimeError(f"❌ MySQL connection error: {e}")


def fetch_table(table_name: str) -> Tuple[List[str], List[tuple]]:
    """
    Fetch all data from a table (backward compatible with old bbdd_query).
    
    Args:
        table_name: Name of the table to fetch
        
    Returns:
        Tuple of (column_names, rows)
    """
    conn = get_connection()
    cursor = conn.cursor()
    
    try:
        query = f"SELECT * FROM {table_name}"
        cursor.execute(query)
        
        # Get column names
        columns = [desc[0] for desc in cursor.description]
        
        # Get all rows
        rows = cursor.fetchall()
        
        return columns, rows
        
    finally:
        cursor.close()
        if conn and conn.is_connected():
            conn.close()
