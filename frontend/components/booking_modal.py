"""
Booking modal component for Property Manager application.

Displays booking details in view or edit mode.
"""
import streamlit as st
from datetime import date
import time
import sys
import os

# Add parent directory to access root services
parent_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, parent_dir)

from shared.database_utils import fetch_table
from ..config import STATUS_OPTIONS, STATUS_COLORS, STATUS_EMOJIS
from ..utils.formatters import format_monetary_value, format_phone_for_whatsapp


def render_booking_detail_view(ev: dict):
    """
    Renders booking details in view-only mode.
    
    Args:
        ev: Event dictionary with extendedProps
    """
    ext = ev.get("extendedProps", {}) or {}
    
    # Main information in columns
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("#### 📅 Stay Dates")
        st.markdown(f"**Check-In:** {ext.get('check_in', 'N/A')}")
        st.markdown(f"**Check-Out:** {ext.get('check_out', 'N/A')}")
        st.markdown(f"**Nights:** {ext.get('nights', 'N/A')}")
        
        st.markdown("#### 👥 Occupancy")
        st.markdown(f"**Persons:** {ext.get('persons', 'N/A')}")
        st.markdown(f"**Adults:** {ext.get('adults', 'N/A')}")
        st.markdown(f"**Children:** {ext.get('children', 'N/A')}")
    
    with col2:
        st.markdown("#### 📋 Booking Information")
        st.markdown(f"**Booking ID:** {ext.get('booking_id', 'N/A')}")
        st.markdown(f"**Booking Number:** {ext.get('booking_number', 'N/A')}")
        st.markdown(f"**Record ID:** {ext.get('record_id', 'N/A')}")
        
        st.markdown("#### 💰 Financial Information")
        price = ext.get('price', 'N/A')
        charges = ext.get('charges', 'N/A')
        electric_allowance = ext.get('electric_allowance', None)
        
        st.markdown(f"**Price:** {format_monetary_value(price)}")
        st.markdown(f"**Comm & Charges:** {format_monetary_value(charges)}")
        st.markdown(f"**Electric Allowance:** {format_monetary_value(electric_allowance)}")
    
    # Contact information
    st.divider()
    st.markdown("#### 📞 Contact Information")
    contact_col1, contact_col2 = st.columns(2)
    
    with contact_col1:
        email = ext.get('email', '')
        if email:
            st.markdown(f"**Email:** [{email}](mailto:{email})")
        else:
            st.markdown("**Email:** Not available")
    
    with contact_col2:
        phone = ext.get('phone', '')
        if phone:
            phone_clean = format_phone_for_whatsapp(phone)
            whatsapp_link = f"https://wa.me/{phone_clean}"
            st.markdown(f"**Mobile:** [📱 {phone}]({whatsapp_link})")
        else:
            st.markdown("**Mobile:** Not available")


def render_booking_detail_edit(ev: dict, record_id):
    """
    Renders booking details in edit mode with form.
    
    Args:
        ev: Event dictionary with extendedProps
        record_id: Database record ID
        
    Returns:
        bool: True if booking was updated successfully
    """
    ext = ev.get("extendedProps", {}) or {}
    
    with st.form("edit_booking_modal"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Stay Dates")
            new_booking_id = st.text_input("Booking ID*", value=ext.get('booking_id', ''))
            new_guest_name = st.text_input("Guest Name*", value=ext.get('guest_name', ''))
            
            # Convert dates
            check_in_str = ext.get('check_in', '')
            check_out_str = ext.get('check_out', '')
            
            try:
                check_in_val = date.fromisoformat(check_in_str) if check_in_str else date.today()
            except:
                check_in_val = date.today()
            
            try:
                check_out_val = date.fromisoformat(check_out_str) if check_out_str else date.today()
            except:
                check_out_val = date.today()
            
            new_check_in = st.date_input("Check-In*", value=check_in_val)
            new_check_out = st.date_input("Check-Out*", value=check_out_val)
            new_nights = (new_check_out - new_check_in).days if new_check_out > new_check_in else 0
            st.info(f"Nights: {new_nights}")
            
            st.markdown("#### 👥 Occupancy")
            new_persons = st.number_input("Persons", min_value=1, value=int(ext.get('persons', 1)))
            new_adults = st.number_input("Adults", min_value=1, value=int(ext.get('adults', 1)))
            new_children = st.number_input("Children", min_value=0, value=int(ext.get('children', 0)))
        
        with col2:
            st.markdown("#### 📋 Booking Information")
            new_booking_number = st.text_input("Booking Number", value=ext.get('booking_number', ''))
            
            current_status = ext.get('status', 'Confirmed')
            try:
                status_index = STATUS_OPTIONS.index(current_status)
            except:
                status_index = 0
            new_status = st.selectbox("Status*", STATUS_OPTIONS, index=status_index)
            
            st.markdown("#### 💰 Financial Information")
            new_price = st.number_input("Price (€)", min_value=0.0, value=float(ext.get('price', 0) if ext.get('price') != 'N/A' else 0), step=10.0)
            new_charges = st.number_input("Comm & Charges (€)", min_value=0.0, value=float(ext.get('charges', 0) if ext.get('charges') != 'N/A' else 0), step=5.0)
            
            st.markdown("#### 📞 Contact")
            new_email = st.text_input("Email", value=ext.get('email', ''))
            new_phone = st.text_input("Mobile", value=ext.get('phone', ''))
        
        col_save, col_cancel = st.columns(2)
        with col_save:
            save_button = st.form_submit_button("💾 Save Changes", use_container_width=True, type="primary")
        with col_cancel:
            cancel_button = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel_button:
            st.session_state.edit_mode = False
            st.rerun()
        
        if save_button:
            if new_booking_id and new_guest_name and new_check_in and new_check_out and new_check_out > new_check_in:
                try:
                    # Use shared database utils (available in both containers)
                    import mysql.connector
                    from shared.constants import get_db_config
                    
                    conn = mysql.connector.connect(**get_db_config())
                    cursor = conn.cursor()
                    
                    query = """
                    UPDATE bookings 
                    SET `Booking ID` = %s, `Nombre,Apellidos` = %s, `Check-In` = %s, `Check-Out` = %s,
                        `Nº Noches` = %s, `Nº Personas` = %s, `Nº Adultos` = %s, `Nº Niños` = %s,
                        `Status` = %s, `Email` = %s, `Movil` = %s, `Precio` = %s, 
                        `Comm y Cargos` = %s, `Nº Booking` = %s
                    WHERE ID = %s
                    """
                    
                    values = (
                        new_booking_id, new_guest_name, new_check_in, new_check_out,
                        new_nights, new_persons, new_adults, new_children,
                        new_status, new_email, new_phone, new_price, new_charges, 
                        new_booking_number, record_id
                    )
                    
                    cursor.execute(query, values)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    st.success(f"✅ Booking {new_booking_id} updated successfully!")
                    
                    # Reload data
                    cols, rows = fetch_table("bookings")
                    st.session_state.db_cols = cols
                    st.session_state.db_rows = rows
                    st.session_state.bookings_data = None
                    st.session_state.edit_mode = False
                    st.session_state.show_modal = False
                    
                    time.sleep(1)
                    st.rerun()
                    
                except Exception as e:
                    st.error(f"❌ Error updating booking: {e}")
            else:
                st.warning("⚠️ Please fill all required fields (*) and ensure check-out is after check-in")


def render_booking_modal(ev: dict):
    """
    Main modal renderer - handles both view and edit modes.
    
    Args:
        ev: Event dictionary with booking data
    """
    ext = ev.get("extendedProps", {}) or {}
    
    # Initialize edit mode in session state
    if 'edit_mode' not in st.session_state:
        st.session_state.edit_mode = False
    
    # Main title with status
    guest_name = ext.get('guest_name', 'Unknown guest')
    status = ext.get('status', '')
    record_id = ext.get('record_id', 'N/A')
    
    # Header with edit button
    col_title, col_edit = st.columns([4, 1])
    with col_title:
        status_emoji = STATUS_EMOJIS.get(status, "📋")
        st.markdown(f"### {status_emoji} {guest_name}")
    with col_edit:
        if not st.session_state.edit_mode:
            if st.button("✏️ Edit", use_container_width=True):
                st.session_state.edit_mode = True
                st.rerun()
        else:
            if st.button("👁️ View", use_container_width=True):
                st.session_state.edit_mode = False
                st.rerun()
    
    if status:
        status_color = STATUS_COLORS.get(status, "#6c757d")
        st.markdown(f'<span style="background-color: {status_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; font-weight: bold;">{status}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # Render view or edit mode
    if not st.session_state.edit_mode:
        render_booking_detail_view(ev)
    else:
        render_booking_detail_edit(ev, record_id)
