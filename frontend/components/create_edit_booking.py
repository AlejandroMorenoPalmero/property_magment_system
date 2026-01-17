"""
Create/Edit Booking component for Property Manager application.

Form to create a new booking or edit an existing one.
"""
import streamlit as st
from datetime import date, timedelta
import sys
import os

# Add parent directory to access shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from shared.database_utils import fetch_table
from ..config import STATUS_OPTIONS
from ..utils.validators import validate_booking_data, calculate_nights


def render_booking_form(mode="create", booking_data=None):
    """
    Renders a form to create or edit a booking.
    
    Args:
        mode: "create" or "edit"
        booking_data: Dict with booking data (for edit mode)
        
    Returns:
        bool: True if booking was saved successfully
    """
    st.subheader(f"{'📝 New Booking' if mode == 'create' else '✏️ Edit Booking'}")
    
    # Get initial values
    if booking_data:
        initial_booking_id = booking_data.get('booking_id', '')
        initial_guest_name = booking_data.get('guest_name', '')
        initial_check_in = date.fromisoformat(booking_data.get('check_in', str(date.today())))
        initial_check_out = date.fromisoformat(booking_data.get('check_out', str(date.today() + timedelta(days=1))))
        initial_persons = booking_data.get('persons', 2)
        initial_adults = booking_data.get('adults', 2)
        initial_children = booking_data.get('children', 0)
        initial_booking_number = booking_data.get('booking_number', '')
        initial_status = booking_data.get('status', 'Confirmed')
        initial_price = booking_data.get('price', 0.0)
        initial_charges = booking_data.get('charges', 0.0)
        initial_email = booking_data.get('email', '')
        initial_phone = booking_data.get('phone', '')
        record_id = booking_data.get('record_id')
    else:
        initial_booking_id = ''
        initial_guest_name = ''
        initial_check_in = date.today()
        initial_check_out = date.today() + timedelta(days=1)
        initial_persons = 2
        initial_adults = 2
        initial_children = 0
        initial_booking_number = ''
        initial_status = 'Confirmed'
        initial_price = 0.0
        initial_charges = 0.0
        initial_email = ''
        initial_phone = ''
        record_id = None
    
    with st.form("booking_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📅 Stay Information")
            booking_id = st.text_input("Booking ID*", value=initial_booking_id, 
                                       help="Unique identifier for this booking")
            guest_name = st.text_input("Guest Name*", value=initial_guest_name,
                                       help="Full name of the guest")
            
            check_in = st.date_input("Check-In Date*", value=initial_check_in,
                                    min_value=date.today() - timedelta(days=365))
            check_out = st.date_input("Check-Out Date*", value=initial_check_out,
                                     min_value=initial_check_in)
            
            nights = calculate_nights(check_in, check_out)
            st.info(f"**Nights:** {nights}")
            
            st.markdown("#### 👥 Occupancy")
            persons = st.number_input("Total Persons*", min_value=1, max_value=20, 
                                     value=initial_persons)
            adults = st.number_input("Adults*", min_value=1, max_value=20, 
                                    value=initial_adults)
            children = st.number_input("Children", min_value=0, max_value=10, 
                                      value=initial_children)
        
        with col2:
            st.markdown("#### 📋 Booking Details")
            booking_number = st.text_input("Booking Number", value=initial_booking_number,
                                          help="Reference number from booking platform")
            
            status_index = STATUS_OPTIONS.index(initial_status) if initial_status in STATUS_OPTIONS else 0
            status = st.selectbox("Status*", STATUS_OPTIONS, index=status_index)
            
            st.markdown("#### 💰 Financial Information")
            price = st.number_input("Price (€)*", min_value=0.0, value=float(initial_price), 
                                   step=10.0, format="%.2f")
            charges = st.number_input("Commission & Charges (€)", min_value=0.0, 
                                     value=float(initial_charges), step=5.0, format="%.2f")
            
            total = price - charges
            st.success(f"**Net Amount:** {total:.2f} €")
            
            st.markdown("#### 📞 Contact Information")
            email = st.text_input("Email", value=initial_email,
                                 placeholder="guest@example.com")
            phone = st.text_input("Mobile", value=initial_phone,
                                 placeholder="+34 600 000 000")
        
        # Form buttons
        col_submit, col_reset = st.columns(2)
        with col_submit:
            submit = st.form_submit_button(
                f"{'💾 Create Booking' if mode == 'create' else '💾 Save Changes'}", 
                use_container_width=True, 
                type="primary"
            )
        with col_reset:
            if mode == "create":
                reset = st.form_submit_button("🔄 Reset Form", use_container_width=True)
            else:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        # Handle form submission
        if submit:
            # Validate
            if validate_booking_data(booking_id, guest_name, check_in, check_out):
                try:
                    # Note: This still uses direct DB access via shared.database_utils
                    # For full API integration, you would need to add create/update endpoints
                    # and use api_client here. For now, keeping shared.database_utils
                    # since it's available in both containers.
                    
                    import mysql.connector
                    from shared.constants import get_db_config
                    
                    conn = mysql.connector.connect(**get_db_config())
                    cursor = conn.cursor()
                    
                    if mode == "create":
                        # INSERT new booking
                        query = """
                        INSERT INTO bookings 
                        (`Booking ID`, `Nombre,Apellidos`, `Check-In`, `Check-Out`, 
                         `Nº Noches`, `Nº Personas`, `Nº Adultos`, `Nº Niños`, 
                         `Status`, `Email`, `Movil`, `Precio`, `Comm y Cargos`, `Nº Booking`)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        """
                        
                        values = (
                            booking_id, guest_name, check_in, check_out,
                            nights, persons, adults, children,
                            status, email, phone, price, charges, booking_number
                        )
                    else:
                        # UPDATE existing booking
                        query = """
                        UPDATE bookings 
                        SET `Booking ID` = %s, `Nombre,Apellidos` = %s, `Check-In` = %s, `Check-Out` = %s,
                            `Nº Noches` = %s, `Nº Personas` = %s, `Nº Adultos` = %s, `Nº Niños` = %s,
                            `Status` = %s, `Email` = %s, `Movil` = %s, `Precio` = %s, 
                            `Comm y Cargos` = %s, `Nº Booking` = %s
                        WHERE ID = %s
                        """
                        
                        values = (
                            booking_id, guest_name, check_in, check_out,
                            nights, persons, adults, children,
                            status, email, phone, price, charges, booking_number,
                            record_id
                        )
                    
                    cursor.execute(query, values)
                    conn.commit()
                    cursor.close()
                    conn.close()
                    
                    # Reload data
                    cols, rows = fetch_table("bookings")
                    st.session_state.db_cols = cols
                    st.session_state.db_rows = rows
                    st.session_state.bookings_data = None
                    
                    st.success(f"✅ Booking {booking_id} {'created' if mode == 'create' else 'updated'} successfully!")
                    st.balloons()
                    
                    return True
                    
                except Exception as e:
                    st.error(f"❌ Error saving booking: {e}")
                    return False
            else:
                st.warning("⚠️ Please fill all required fields (*) and ensure check-out is after check-in")
                return False
        
        return False


def render_create_edit_page():
    """
    Main page for creating or editing bookings.
    """
    st.title("📝 Manage Bookings")
    
    # Mode selector
    mode = st.radio(
        "Choose action:",
        ["Create New Booking", "Edit Existing Booking"],
        horizontal=True
    )
    
    st.divider()
    
    if mode == "Create New Booking":
        render_booking_form(mode="create")
    
    else:  # Edit Existing Booking
        st.subheader("🔍 Find Booking to Edit")
        
        # Search options
        search_by = st.selectbox(
            "Search by:",
            ["Booking ID", "Guest Name", "Record ID"]
        )
        
        search_value = st.text_input(f"Enter {search_by}:")
        
        if st.button("🔎 Search", use_container_width=True):
            if search_value:
                try:
                    # Load all bookings and search in memory
                    columns, rows = fetch_table("bookings")
                    col_map = {col: idx for idx, col in enumerate(columns)}
                    
                    result = None
                    if search_by == "Booking ID":
                        for row in rows:
                            if row[col_map['Booking ID']] == search_value:
                                result = row
                                break
                    elif search_by == "Guest Name":
                        for row in rows:
                            if search_value.lower() in str(row[col_map['Nombre,Apellidos']]).lower():
                                result = row
                                break
                    else:  # Record ID
                        for row in rows:
                            if str(row[col_map['ID']]) == search_value:
                                result = row
                                break
                    
                    if result:
                        booking_data = {
                            'record_id': result[col_map['ID']],
                            'booking_id': result[col_map['Booking ID']],
                            'guest_name': result[col_map['Nombre,Apellidos']],
                            'check_in': str(result[col_map['Check-In']]),
                            'check_out': str(result[col_map['Check-Out']]),
                            'persons': result[col_map['Nº Personas']],
                            'adults': result[col_map['Nº Adultos']],
                            'children': result[col_map['Nº Niños']],
                            'booking_number': result[col_map['Nº Booking']],
                            'status': result[col_map['Status']],
                            'price': result[col_map['Precio']],
                            'charges': result[col_map['Comm y Cargos']],
                            'email': result[col_map['Email']],
                            'phone': result[col_map['Movil']],
                        }
                        
                        st.session_state['edit_booking_data'] = booking_data
                        st.success(f"✅ Found booking: {booking_data['guest_name']}")
                    else:
                        st.warning(f"⚠️ No booking found with {search_by}: {search_value}")
                    
                except Exception as e:
                    st.error(f"❌ Error searching: {e}")
            else:
                st.warning("⚠️ Please enter a search value")
        
        # Show edit form if booking is found
        if 'edit_booking_data' in st.session_state:
            st.divider()
            render_booking_form(mode="edit", booking_data=st.session_state['edit_booking_data'])
