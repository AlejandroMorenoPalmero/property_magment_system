"""
Booking service for Property Manager application.

Business logic for loading, filtering, and managing bookings.
"""
import sys
import os
from datetime import date

# Add parent directory to access root services
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from shared.database_utils import fetch_table
from .data_transformer import convert_db_to_dataframe, add_electric_allowance


def load_bookings(start_date: date, end_date: date):
    """
    Loads and filters bookings from database for the given date range.
    
    Args:
        start_date: Filter start date
        end_date: Filter end date
        
    Returns:
        dict: Dictionary with 'df' (DataFrame), 'count', 'start_date', 'end_date'
              or None if no data found
    """
    try:
        # Load fresh data from DB
        cols_fresh, rows_fresh = fetch_table("bookings")
        
        if not rows_fresh:
            return None
        
        # Convert to DataFrame with filtering
        df = convert_db_to_dataframe(cols_fresh, rows_fresh, start_date, end_date)
        
        if df.empty:
            return None
        
        # Add electric allowance column
        df = add_electric_allowance(df)
        
        return {
            'df': df,
            'count': len(df),
            'start_date': start_date,
            'end_date': end_date
        }
        
    except Exception as e:
        print(f"🚨 Error loading bookings: {e}")
        return None


def auto_load_bookings_if_needed(start_date: date, end_date: date, session_state):
    """
    Auto-loads bookings data if table is visible but data is not loaded.
    
    Args:
        start_date: Filter start date
        end_date: Filter end date
        session_state: Streamlit session state object
    """
    if session_state.bookings_table_visible and session_state.bookings_data is None:
        try:
            bookings_data = load_bookings(start_date, end_date)
            if bookings_data:
                session_state.bookings_data = bookings_data
            else:
                session_state.bookings_table_visible = False
        except Exception as e:
            # If auto-load fails, silently disable table
            session_state.bookings_table_visible = False
