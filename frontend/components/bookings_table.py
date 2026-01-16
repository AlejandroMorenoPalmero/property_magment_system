"""
Bookings table component for Property Manager application.

Displays a custom-styled table of bookings with view buttons.
"""
import streamlit as st
import pandas as pd
from datetime import date
from ..styles.custom_styles import get_table_styles
from ..config import TABLE_HEADER_LABELS, CHECKOUT_SOON_DAYS, CHECKIN_SOON_DAYS


def render_bookings_table(df: pd.DataFrame) -> dict:
    """
    Renders a custom-styled bookings table with action buttons.
    
    Args:
        df: DataFrame with booking data
        
    Returns:
        dict: Selected event data if button clicked, None otherwise
    """
    selected_event = None
    
    # Inject CSS styles
    st.markdown(get_table_styles(), unsafe_allow_html=True)
    
    # Container for table
    st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
    
    # Table header - using columns
    header_cols = st.columns([1.5, 2.5, 1.5, 1.5, 1, 1.2])
    for col, label in zip(header_cols, TABLE_HEADER_LABELS):
        with col:
            st.markdown(f'<div class="custom-table-header">{label}</div>', unsafe_allow_html=True)
    
    # Table rows
    for idx, row_data in df.iterrows():
        # Determine row class based on dates
        row_class = ""
        try:
            checkout_str = row_data['Check-Out']
            checkin_str = row_data['Check-In']
            
            if isinstance(checkout_str, str):
                checkout_date = date.fromisoformat(checkout_str)
            else:
                checkout_date = checkout_str
                
            if isinstance(checkin_str, str):
                checkin_date = date.fromisoformat(checkin_str)
            else:
                checkin_date = checkin_str
            
            days_until_checkout = (checkout_date - date.today()).days
            days_until_checkin = (checkin_date - date.today()).days
            
            if days_until_checkout <= CHECKOUT_SOON_DAYS:
                row_class = "row-checkout-soon"
            elif (days_until_checkin <= CHECKIN_SOON_DAYS) and (days_until_checkin >= 0):
                row_class = "row-checkin-soon"
        except:
            pass
        
        # Create columns for each row
        row_cols = st.columns([1.5, 2.5, 1.5, 1.5, 1, 1.2])
        
        # Determine cell background color based on dates
        cell_bg = ""
        if row_class == "row-checkout-soon":
            cell_bg = "background-color: #ffebee;"
        elif row_class == "row-checkin-soon":
            cell_bg = "background-color: #e8f5e9;"
        
        with row_cols[0]:
            st.markdown(f'<div class="custom-table-cell" style="{cell_bg}"><span class="booking-id">{row_data["Booking ID"]}</span></div>', unsafe_allow_html=True)
        
        with row_cols[1]:
            st.markdown(f'<div class="custom-table-cell" style="{cell_bg}">{row_data["Name and Surname"]}</div>', unsafe_allow_html=True)
        
        with row_cols[2]:
            st.markdown(f'<div class="custom-table-cell" style="{cell_bg}">{row_data["Check-In"]}</div>', unsafe_allow_html=True)
        
        with row_cols[3]:
            st.markdown(f'<div class="custom-table-cell" style="{cell_bg}">{row_data["Check-Out"]}</div>', unsafe_allow_html=True)
        
        with row_cols[4]:
            st.markdown(f'<div class="custom-table-cell" style="{cell_bg}"><span class="badge-nights">{row_data["Nº Nights"]} nights</span></div>', unsafe_allow_html=True)
        
        with row_cols[5]:
            if st.button("📋 View", key=f"btn_view_{idx}", use_container_width=True):
                # Create event object from DataFrame row
                selected_event = {
                    "id": f"booking-{row_data.get('Record ID', idx)}",
                    "title": f"{row_data['Name and Surname']}",
                    "start": row_data['Check-In'],
                    "end": row_data['Check-Out'],
                    "extendedProps": {
                        "record_id": row_data.get('Record ID', 'N/A'),
                        "booking_id": row_data['Booking ID'],
                        "booking_number": row_data.get('Booking Number', 'N/A'),
                        "guest_name": row_data['Name and Surname'],
                        "check_in": row_data['Check-In'],
                        "check_out": row_data['Check-Out'],
                        "status": row_data.get('Status', 'N/A'),
                        "nights": row_data['Nº Nights'],
                        "persons": row_data.get('Persons', 'N/A'),
                        "adults": row_data.get('Adults', 'N/A'),
                        "children": row_data.get('Children', 'N/A'),
                        "email": row_data.get('Email', ''),
                        "phone": row_data.get('Phone', ''),
                        "price": row_data.get('Price', 'N/A'),
                        "charges": row_data.get('Charges', 'N/A'),
                        "electric_allowance": row_data.get('Allowance electric', 'N/A'),
                        "source": "table_button"
                    }
                }
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)
    
    return selected_event
