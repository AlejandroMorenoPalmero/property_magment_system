"""
Calendar view component for Property Manager application.

Displays an interactive FullCalendar with booking events.
"""
import streamlit as st
from streamlit_calendar import calendar
from streamlit_javascript import st_javascript
from datetime import date
from ..styles.custom_styles import get_calendar_styles
from ..config import CALENDAR_CONFIG, CALENDAR_MONTHS_ES
from ..utils.formatters import click_token


def render_calendar_navigation():
    """
    Renders calendar navigation controls (month/year selector + today button).
    
    Returns:
        tuple: (selected_month, selected_year)
    """
    # Initialize calendar navigation state
    if 'calendar_month' not in st.session_state:
        st.session_state.calendar_month = date.today().month
    if 'calendar_year' not in st.session_state:
        st.session_state.calendar_year = date.today().year

    # Calendar navigation controls
    nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([2, 2, 1, 3])

    with nav_col1:
        selected_month = st.selectbox(
            "Mes:",
            options=list(CALENDAR_MONTHS_ES.keys()),
            format_func=lambda x: CALENDAR_MONTHS_ES[x],
            index=st.session_state.calendar_month - 1,
            key="month_selector"
        )
        if selected_month != st.session_state.calendar_month:
            st.session_state.calendar_month = selected_month
            st.rerun()

    with nav_col2:
        # Generate year range (current year ± 5 years)
        current_year = date.today().year
        year_range = list(range(current_year - 2, current_year + 5))
        selected_year = st.selectbox(
            "Año:",
            options=year_range,
            index=year_range.index(st.session_state.calendar_year),
            key="year_selector",
            label_visibility="visible"
        )
        if selected_year != st.session_state.calendar_year:
            st.session_state.calendar_year = selected_year
            st.rerun()

    with nav_col3:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("📅 Hoy", use_container_width=True):
            st.session_state.calendar_month = date.today().month
            st.session_state.calendar_year = date.today().year
            st.rerun()
    
    return selected_month, selected_year


def render_calendar(events: list, month: int = None, year: int = None) -> dict:
    """
    Renders the FullCalendar component with events.
    
    Args:
        events: List of event dictionaries for FullCalendar
        month: Month to display (1-12), defaults to current month
        year: Year to display, defaults to current year
        
    Returns:
        dict: Clicked event data if any, None otherwise
    """
    # Get viewport dimensions
    viewport_width = st_javascript("window.innerWidth", key="viewport_width")
    
    # Use provided month/year or defaults from session state
    if month is None:
        month = st.session_state.get('calendar_month', date.today().month)
    if year is None:
        year = st.session_state.get('calendar_year', date.today().year)
    
    # Calculate initial date for calendar
    initial_date = date(year, month, 1).isoformat()
    
    # Calendar options
    options = {
        "initialView": CALENDAR_CONFIG["initial_view"],
        "initialDate": initial_date,
        "locale": CALENDAR_CONFIG["locale"],
        "firstDay": CALENDAR_CONFIG["first_day"],
        "headerToolbar": {
            "left": "prev,next",
            "center": "title",
            "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
        },
        "height": CALENDAR_CONFIG["height"],
        "weekNumbers": True,
        "selectable": True,
        "navLinks": True,
    }
    
    # Get dynamic CSS styles
    custom_css = get_calendar_styles(viewport_width)
    
    # Print viewport debug only once
    if viewport_width and 'viewport_debug' not in st.session_state:
        st.session_state.viewport_debug = True
        print(f"🔍 Debug viewport: {viewport_width*0.3/7}")
    
    # Render calendar with dynamic key
    calendar_key = f"cal_{year}_{month}"
    returned = calendar(events=events, options=options, key=calendar_key, custom_css=custom_css)
    
    # Capture clicks
    clicked = None
    if isinstance(returned, dict):
        if "eventClick" in returned and isinstance(returned["eventClick"], dict):
            clicked = returned["eventClick"].get("event")
        if not clicked and "clickedEvent" in returned:
            clicked = returned["clickedEvent"]
    
    # Process clicked event
    if clicked:
        token = click_token(clicked)
        if token and token != st.session_state.get("last_click_token"):
            st.session_state["last_click_token"] = token
            return clicked
    
    return None
