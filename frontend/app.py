# app.py
"""
Property Manager - Main Application
Refactored version using modular components.
"""
import streamlit as st
from datetime import date, timedelta
import sys
import os

# Setup paths for imports
import pathlib
current_dir = pathlib.Path(__file__).parent  # frontend/
parent_dir = current_dir.parent  # project root

# Add parent directory FIRST (for shared modules)
sys.path.insert(0, str(parent_dir))

# Import from shared utilities (backward compatible)
from shared.database_utils import fetch_table

# Now add current directory for frontend modules
sys.path.insert(0, str(current_dir))

# Import frontend modules using relative imports to avoid conflicts
from frontend.config import APP_TITLE, APP_VERSION
from frontend.services.state_manager import initialize_session_state, load_db_data_once, reset_bookings_state
from frontend.services.booking_service import load_bookings, auto_load_bookings_if_needed
from frontend.services.data_transformer import convert_db_to_events, fix_calendar_events_dates
from frontend.components.date_range_selector import render_date_range_selector
from frontend.components.bookings_table import render_bookings_table
from frontend.components.calendar_view import render_calendar_navigation, render_calendar
from frontend.components.booking_modal import render_booking_modal
from frontend.components.create_edit_booking import render_create_edit_page
from frontend.components.search_bookings import render_search_bookings_page


# ============================================================================
# INITIALIZATION
# ============================================================================

# Configure page FIRST (must be first Streamlit call)
st.set_page_config(
    page_title=APP_TITLE, 
    page_icon="🏠", 
    layout="wide",
    initial_sidebar_state="expanded"  # Sidebar expandido por defecto
)

# Initialize session state
initialize_session_state()

# Load database data once
load_db_data_once(fetch_table)


# ============================================================================
# SIDEBAR NAVIGATION
# ============================================================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/619/619032.png", width=80)
    st.title("🏠 Property Manager")
    st.divider()
    
    # Navigation
    page = st.radio(
        "Navigate to:",
        ["📋 Bookings Overview", "🔍 Search Bookings", "📝 Manage Bookings"],
        label_visibility="collapsed"
    )
    
    st.divider()
    
    # Quick stats
    if 'db_rows' in st.session_state and st.session_state.db_rows:
        total_bookings = len(st.session_state.db_rows)
        st.metric("Total Bookings", total_bookings)
    
    # Footer
    st.markdown("---")
    st.caption("Property Management System")


# ============================================================================
# MAIN CONTENT - ROUTING
# ============================================================================

if page == "📋 Bookings Overview":
    # ========================================================================
    # BOOKINGS OVERVIEW PAGE
    # ========================================================================
    # ========================================================================
    # BOOKINGS OVERVIEW PAGE
    # ========================================================================
    
    st.title("📋 Bookings Overview")
    st.write("")
    
    # BOOKINGS TABLE SECTION
    st.subheader("📋 Bookings")
    
    # Date range selector
    start_date, end_date, date_mode = render_date_range_selector()
    
    # Auto-load bookings if needed
    auto_load_bookings_if_needed(start_date, end_date, st.session_state)
    
    # Load/Refresh and Hide buttons
    colA, colB = st.columns([1, 3], vertical_alignment="center")
    with colA:
        cargar = st.button("Load/Refresh bookings", use_container_width=True)
    
    with colB:
        if st.session_state.bookings_table_visible:
            if st.button("Hide table"):
                st.session_state.bookings_table_visible = False
                st.session_state.bookings_data = None
                st.rerun()
    
    # Handle load button click
    if cargar:
        bookings_data = load_bookings(start_date, end_date)
        
        if bookings_data:
            st.session_state.bookings_data = bookings_data
            st.session_state.bookings_table_visible = True
            st.success(f"✅ Found {bookings_data['count']} bookings from {start_date} to {end_date}")
            st.rerun()
        else:
            st.info(f"No bookings scheduled from {start_date} to {end_date}")
            st.session_state.bookings_table_visible = False
    
    # Display table if visible
    if st.session_state.bookings_table_visible and st.session_state.bookings_data:
        data = st.session_state.bookings_data
        df = data['df'].copy()
        
        # Render table and capture click
        selected_event = render_bookings_table(df)
        
        if selected_event:
            st.session_state["selected_event"] = selected_event
            st.session_state["show_modal"] = True
            st.rerun()
    
    # CALENDAR SECTION
    st.subheader("🗓️ Calendar with events (click an event)")
    
    # Render calendar navigation
    selected_month, selected_year = render_calendar_navigation()
    
    # Convert DB data to events
    if 'db_rows' in st.session_state and st.session_state.db_rows:
        events = convert_db_to_events(st.session_state.db_cols, st.session_state.db_rows)
        print(f"✅ Converted {len(events)} events from database")
    else:
        # Fallback: example events if no DB data
        events = [
            {
                "id": "fallback-1",
                "title": "No DB data - Example",
                "start": date.today().isoformat(),
                "end": (date.today() + timedelta(days=2)).isoformat(),
                "allDay": True,
                "classNames": ["reserva"],
                "extendedProps": {
                    "tipo": "fallback",
                    "nota": "Connect database to see real bookings"
                }
            }
        ]
        print("⚠️ Using fallback events - no DB data")
    
    # Fix calendar event dates
    events_fixed = fix_calendar_events_dates(events)
    
    # Render calendar and capture click
    clicked_event = render_calendar(events_fixed, selected_month, selected_year)
    
    if clicked_event:
        st.session_state["selected_event"] = clicked_event
        st.session_state["show_modal"] = True
        st.rerun()
    
    # MODAL SECTION
    _has_dialog = hasattr(st, "dialog")
    
    if st.session_state.get("show_modal") and st.session_state.get("selected_event") and _has_dialog:
        @st.dialog("Event Details", width="small")
        def _show_event_dialog():
            render_booking_modal(st.session_state["selected_event"])
            
            # Show close button only in view mode
            if not st.session_state.get('edit_mode', False):
                st.divider()
                if st.button("Close", use_container_width=True):
                    st.session_state["show_modal"] = False
                    st.session_state.edit_mode = False
                    st.rerun()
        
        _show_event_dialog()
    
    elif st.session_state.get("selected_event") and not _has_dialog:
        # Fallback for older Streamlit versions
        st.warning("Your Streamlit version doesn't support `st.dialog`. Showing detail inline.")
        render_booking_modal(st.session_state["selected_event"])

elif page == "🔍 Search Bookings":
    # ========================================================================
    # SEARCH BOOKINGS PAGE
    # ========================================================================
    
    render_search_bookings_page()

else:
    # ========================================================================
    # MANAGE BOOKINGS PAGE (Create/Edit)
    # ========================================================================
    
    render_create_edit_page()
