"""
Date range selector component for Property Manager application.

Provides UI for selecting date ranges in two modes:
- Next N days from today
- Custom date range
"""
import streamlit as st
from datetime import date, timedelta
from ..config import DATE_RANGE_MODES, DEFAULT_DATE_RANGE_DAYS


def render_date_range_selector() -> tuple:
    """
    Renders date range selection UI with two modes.
    
    Returns:
        tuple: (start_date, end_date, mode)
    """
    # Initialize date range in session state if not exists
    if 'date_range_days' not in st.session_state:
        st.session_state.date_range_days = DEFAULT_DATE_RANGE_DAYS
    if 'custom_start_date' not in st.session_state:
        st.session_state.custom_start_date = None
    if 'custom_end_date' not in st.session_state:
        st.session_state.custom_end_date = None

    # Date range selection
    col_selector1, col_selector2, col_selector3 = st.columns([2, 2, 2])

    with col_selector1:
        date_mode = st.radio(
            "Date range mode:",
            DATE_RANGE_MODES,
            horizontal=True,
            key="date_mode"
        )

    if date_mode == "Next days":
        with col_selector2:
            days = st.number_input(
                "Days from today:",
                min_value=1,
                max_value=365,
                value=st.session_state.date_range_days,
                step=7,
                key="days_input"
            )
            st.session_state.date_range_days = days
        
        with col_selector3:
            st.markdown(f"**From:** {date.today().strftime('%Y-%m-%d')}")
            st.markdown(f"**To:** {(date.today() + timedelta(days=days)).strftime('%Y-%m-%d')}")
        
        start_date = date.today()
        end_date = start_date + timedelta(days=days)
    
    else:  # Custom dates
        with col_selector2:
            start_date = st.date_input(
                "Start date:",
                value=st.session_state.custom_start_date or date.today(),
                key="start_date_input"
            )
            st.session_state.custom_start_date = start_date
        
        with col_selector3:
            end_date = st.date_input(
                "End date:",
                value=st.session_state.custom_end_date or (date.today() + timedelta(days=DEFAULT_DATE_RANGE_DAYS)),
                min_value=start_date,
                key="end_date_input"
            )
            st.session_state.custom_end_date = end_date
    
    return start_date, end_date, date_mode
