"""
Extract data from the database tables.
"""

from services.bbdd_conection import get_connection


def fetch_table(table_name='bookings', limit=None):
    conn = get_connection()
    cur = conn.cursor()

    try:
        query = f"SELECT * FROM {table_name}"
        if limit:
            query += f" LIMIT {limit}"
        
        cur.execute(query)
        rows = cur.fetchall()
        columns = [desc[0] for desc in cur.description]

        return columns, rows

    finally:
        cur.close()
        conn.close()
