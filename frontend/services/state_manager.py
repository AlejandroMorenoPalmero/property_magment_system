"""
Session state management for Property Manager application.

Functions for initializing and managing Streamlit session state.
"""
import streamlit as st
from datetime import date


def initialize_session_state():
    """
    Initializes all session state variables with default values.
    Should be called once at app startup.
    """
    # Get today's date for calendar initialization
    today = date.today()
    
    defaults = {
        "selected_event": None,
        "show_modal": False,
        "last_click_token": None,
        "bookings_table_visible": True,
        "bookings_data": None,
        "date_range_days": 14,
        "custom_start_date": None,
        "custom_end_date": None,
        "calendar_month": today.month,
        "calendar_year": today.year,
        "edit_mode": False,
    }
    
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_bookings_state():
    """
    Resets all bookings-related session state variables.
    Useful after data updates or when refreshing bookings.
    """
    st.session_state.bookings_data = None
    st.session_state.bookings_table_visible = False


def load_db_data_once(fetch_function):
    """
    Loads database data once and stores in session state.
    
    Args:
        fetch_function: Function to call to fetch data (should return cols, rows)
    """
    if 'db_data_loaded' not in st.session_state:
        cols, rows = fetch_function("bookings")
        st.session_state.db_data_loaded = True
        st.session_state.db_cols = cols
        st.session_state.db_rows = rows
