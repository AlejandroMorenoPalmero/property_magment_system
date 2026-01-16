"""
Data conversion utilities for Property Manager application.

Functions for converting between different data types and formats,
particularly for database values and date handling.
"""
from decimal import Decimal
from datetime import date


def safe_convert_value(value):
    """
    Converts problematic values for JSON serialization.
    
    Args:
        value: Any value from database or data structure
        
    Returns:
        Converted value safe for JSON serialization
    """
    if isinstance(value, Decimal):
        return float(value)
    elif hasattr(value, 'date'):  # datetime objects
        return value.date().isoformat()
    elif value is None:
        return None
    else:
        return value


def convert_date_field(value):
    """
    Converts any date format to a Python date object.
    
    Args:
        value: Can be str (ISO format), datetime, or date object
        
    Returns:
        date object or original value if conversion fails
    """
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except (ValueError, TypeError):
            return value
    elif hasattr(value, 'date'):  # datetime object
        return value.date()
    else:
        return value


def is_date_only(iso_str: str) -> bool:
    """
    Check if date string is in date-only format (YYYY-MM-DD).
    
    Args:
        iso_str: ISO formatted date string
        
    Returns:
        True if format is date-only (no time component)
    """
    return isinstance(iso_str, str) and "T" not in iso_str
