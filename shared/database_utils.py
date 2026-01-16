"""
Shared database utilities for backward compatibility.
Provides simple database access functions for frontend.
"""

import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from backend.database.connection import get_connection
from typing import List, Tuple


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
