# app.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_calendar import calendar
from streamlit_javascript import st_javascript
from services.bbdd_query import fetch_table
from services.bbdd_conection import get_connection
import mysql.connector
from decimal import Decimal
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

# ---------------- Helper Functions ----------------
def safe_convert_value(value):
    """
    Converts problematic values for JSON serialization
    """
    if isinstance(value, Decimal):
        return float(value)
    elif hasattr(value, 'date'):  # datetime objects
        return value.date().isoformat()
    elif value is None:
        return None
    else:
        return value

# Execute only once using session_state
if 'db_data_loaded' not in st.session_state:
    cols, rows = fetch_table("bookings")
    st.session_state.db_data_loaded = True
    st.session_state.db_cols = cols
    st.session_state.db_rows = rows



# ---------------- Config ----------------
st.set_page_config(page_title="Property Manager", page_icon="🏠", layout="wide")

# ---------------- State ----------------
for k, v in {
    "selected_event": None,
    "show_modal": False,
    "last_click_token": None,
    "bookings_table_visible": True,  # Default to True to show table by default
    "bookings_data": None,
}.items():
    st.session_state.setdefault(k, v)

# ---------------- Header ----------------
st.title("🏠 Property Manager")
st.caption("Version 0.0.1")

# ---------------- Bookings table (next 2 weeks) ----------------
st.subheader("📋 Bookings")

# Initialize date range in session state if not exists
if 'date_range_days' not in st.session_state:
    st.session_state.date_range_days = 14  # Default 2 weeks
if 'custom_start_date' not in st.session_state:
    st.session_state.custom_start_date = None
if 'custom_end_date' not in st.session_state:
    st.session_state.custom_end_date = None

# Date range selection
col_selector1, col_selector2, col_selector3 = st.columns([2, 2, 2])

with col_selector1:
    date_mode = st.radio(
        "Date range mode:",
        ["Next days", "Custom dates"],
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
else:
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
            value=st.session_state.custom_end_date or (date.today() + timedelta(days=14)),
            min_value=start_date,
            key="end_date_input"
        )
        st.session_state.custom_end_date = end_date

# Auto-load bookings data if not already loaded
if st.session_state.bookings_table_visible and st.session_state.bookings_data is None:
    # Calculate date range based on mode
    if date_mode == "Next days":
        today = date.today()
        end_date = today + timedelta(days=st.session_state.date_range_days)
    else:
        today = st.session_state.custom_start_date
        end_date = st.session_state.custom_end_date
    
    try:
        # Load fresh data from DB
        cols_fresh, rows_fresh = fetch_table("bookings")
        
        if rows_fresh:
            # Filter by dates - include:
            # 1. Active reservations (check-in <= today <= check-out)
            # 2. Check-ins from today to +2 weeks
            # 3. Check-outs from today to +2 weeks
            col_map = {col: idx for idx, col in enumerate(cols_fresh)}
            filtered_rows = []
            
            for row in rows_fresh:
                try:
                    check_in_raw = row[col_map.get('Check-In')]
                    check_out_raw = row[col_map.get('Check-Out')]
                    
                    # Convert dates
                    if isinstance(check_in_raw, str):
                        check_in = date.fromisoformat(check_in_raw)
                    elif hasattr(check_in_raw, 'date'):
                        check_in = check_in_raw.date()
                    else:
                        check_in = check_in_raw
                    
                    if isinstance(check_out_raw, str):
                        check_out = date.fromisoformat(check_out_raw)
                    elif hasattr(check_out_raw, 'date'):
                        check_out = check_out_raw.date()
                    else:
                        check_out = check_out_raw
                    
                    # Filter logic: Include bookings that:
                    # 1. Are currently active: check_in <= today <= check_out
                    # 2. Have chey to +2 weeks: today <= check_out <= end_date
                    # 4. Overlap with the perck-in from today to +2 weeks: today <= check_in <= end_date
                    # 3. Have check-out from todaiod: check_in <= end_date AND check_out >= today
                    
                    is_currently_active = check_in <= today <= check_out
                    has_checkin_in_period = today <= check_in <= end_date
                    has_checkout_in_period = today <= check_out <= end_date
                    overlaps_period = check_in <= end_date and check_out >= today
                    
                    if is_currently_active or has_checkin_in_period or has_checkout_in_period or overlaps_period:
                        filtered_rows.append(row)
                        
                except Exception as e:
                    continue
            
            if filtered_rows:
                # Create DataFrame with the specific columns requested
                booking_data = []
                for row in filtered_rows:
                    try:
                        # Extract all data from DB row
                        record_id = safe_convert_value(row[col_map.get('ID')])
                        booking_id = safe_convert_value(row[col_map.get('Booking ID')])
                        guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos')]) or "No name"
                        check_in = row[col_map.get('Check-In')]
                        check_out = row[col_map.get('Check-Out')]
                        nights = safe_convert_value(row[col_map.get('Nº Noches')])
                        persons = safe_convert_value(row[col_map.get('Nº Personas')])
                        adults = safe_convert_value(row[col_map.get('Nº Adultos')])
                        children = safe_convert_value(row[col_map.get('Nº Niños')])
                        booking_number = safe_convert_value(row[col_map.get('Nº Booking')])
                        status = safe_convert_value(row[col_map.get('Status')])
                        email = safe_convert_value(row[col_map.get('Email')])
                        phone = safe_convert_value(row[col_map.get('Movil')])
                        charges = safe_convert_value(row[col_map.get('Comm y Cargos')])
                        price = safe_convert_value(row[col_map.get('Precio')])
                        
                        # Convert dates for display
                        if isinstance(check_in, str):
                            check_in_display = check_in
                        elif hasattr(check_in, 'date'):
                            check_in_display = check_in.date().isoformat()
                        else:
                            check_in_display = str(check_in)
                            
                        if isinstance(check_out, str):
                            check_out_display = check_out
                        elif hasattr(check_out, 'date'):
                            check_out_display = check_out.date().isoformat()
                        else:
                            check_out_display = str(check_out)
                        
                        booking_data.append({
                            "Record ID": record_id,
                            "Booking ID": booking_id,
                            "Booking Number": booking_number,
                            "Name and Surname": guest_name,
                            "Check-In": check_in_display,
                            "Check-Out": check_out_display,
                            "Nº Nights": nights,
                            "Status": status,
                            "Persons": persons,
                            "Adults": adults,
                            "Children": children,
                            "Email": email,
                            "Phone": phone,
                            "Price": price,
                            "Charges": charges
                        })
                    except Exception as e:
                        continue
                
                if booking_data:
                    df = pd.DataFrame(booking_data)
                    # Save in session_state
                    st.session_state.bookings_data = {
                        'df': df,
                        'count': len(booking_data),
                        'start_date': today,
                        'end_date': end_date
                    }
    except Exception as e:
        # If auto-load fails, just continue without showing error
        st.session_state.bookings_table_visible = False

colA, colB = st.columns([1, 3], vertical_alignment="center")
with colA:
    cargar = st.button("Load/Refresh bookings", use_container_width=True)
    
with colB:
    if st.session_state.bookings_table_visible:
        if st.button("Hide table"):
            st.session_state.bookings_table_visible = False
            st.session_state.bookings_data = None
            st.rerun()

if cargar:
    try:
        # Calculate date range based on mode
        if st.session_state.date_mode == "Next days":
            today = date.today()
            end_date = today + timedelta(days=st.session_state.date_range_days)
        else:
            today = st.session_state.custom_start_date
            end_date = st.session_state.custom_end_date
        
        # Load fresh data from DB
        cols_fresh, rows_fresh = fetch_table("bookings")  
        
        if rows_fresh:
            # Filter by dates - include:
            # 1. Active reservations (check-in <= today <= check-out)
            # 2. Check-ins from today to +2 weeks
            # 3. Check-outs from today to +2 weeks
            col_map = {col: idx for idx, col in enumerate(cols_fresh)}
            filtered_rows = []
            
            for row in rows_fresh:
                try:
                    check_in_raw = row[col_map.get('Check-In')]
                    check_out_raw = row[col_map.get('Check-Out')]
                    
                    # Convert dates
                    if isinstance(check_in_raw, str):
                        check_in = date.fromisoformat(check_in_raw)
                    elif hasattr(check_in_raw, 'date'):
                        check_in = check_in_raw.date()
                    else:
                        check_in = check_in_raw
                    
                    if isinstance(check_out_raw, str):
                        check_out = date.fromisoformat(check_out_raw)
                    elif hasattr(check_out_raw, 'date'):
                        check_out = check_out_raw.date()
                    else:
                        check_out = check_out_raw
                    
                    # Filter logic: Include bookings that:
                    # 1. Are currently active: check_in <= today <= check_out
                    # 2. Have check-in from today to +2 weeks: today <= check_in <= end_date
                    # 3. Have check-out from today to +2 weeks: today <= check_out <= end_date
                    # 4. Overlap with the period: check_in <= end_date AND check_out >= today
                    
                    is_currently_active = check_in <= today <= check_out
                    has_checkin_in_period = today <= check_in <= end_date
                    has_checkout_in_period = today <= check_out <= end_date
                    overlaps_period = check_in <= end_date and check_out >= today
                    
                    if is_currently_active or has_checkin_in_period or has_checkout_in_period or overlaps_period:
                        filtered_rows.append(row)
                        
                except Exception as e:
                    print(f"⚠️ Error processing date in row: {e}")
                    continue
            
            if filtered_rows:
                # Create DataFrame with the specific columns requested
                booking_data = []
                for row in filtered_rows:
                    try:
                        # Extract all data from DB row
                        record_id = safe_convert_value(row[col_map.get('ID')])
                        booking_id = safe_convert_value(row[col_map.get('Booking ID')])
                        guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos')]) or "No name"
                        check_in = row[col_map.get('Check-In')]
                        check_out = row[col_map.get('Check-Out')]
                        nights = safe_convert_value(row[col_map.get('Nº Noches')])
                        persons = safe_convert_value(row[col_map.get('Nº Personas')])
                        adults = safe_convert_value(row[col_map.get('Nº Adultos')])
                        children = safe_convert_value(row[col_map.get('Nº Niños')])
                        booking_number = safe_convert_value(row[col_map.get('Nº Booking')])
                        status = safe_convert_value(row[col_map.get('Status')])
                        email = safe_convert_value(row[col_map.get('Email')])
                        phone = safe_convert_value(row[col_map.get('Movil')])
                        charges = safe_convert_value(row[col_map.get('Comm y Cargos')])
                        price = safe_convert_value(row[col_map.get('Precio')])
                        
                        # Convert dates for display
                        if isinstance(check_in, str):
                            check_in_display = check_in
                        elif hasattr(check_in, 'date'):
                            check_in_display = check_in.date().isoformat()
                        else:
                            check_in_display = str(check_in)
                            
                        if isinstance(check_out, str):
                            check_out_display = check_out
                        elif hasattr(check_out, 'date'):
                            check_out_display = check_out.date().isoformat()
                        else:
                            check_out_display = str(check_out)
                        
                        booking_data.append({
                            "Record ID": record_id,
                            "Booking ID": booking_id,
                            "Booking Number": booking_number,
                            "Name and Surname": guest_name,
                            "Check-In": check_in_display,
                            "Check-Out": check_out_display,
                            "Nº Nights": nights,
                            "Status": status,
                            "Persons": persons,
                            "Adults": adults,
                            "Children": children,
                            "Email": email,
                            "Phone": phone,
                            "Price": price,
                            "Charges": charges
                        })
                    except Exception as e:
                        print(f"⚠️ Error creating row for table: {e}")
                        continue
                
                if booking_data:
                    df = pd.DataFrame(booking_data)
                    # Save in session_state to keep visible
                    st.session_state.bookings_data = {
                        'df': df,
                        'count': len(booking_data),
                        'start_date': today,
                        'end_date': end_date
                    }
                    st.session_state.bookings_table_visible = True
                    st.success(f"✅ Found {len(booking_data)} bookings from {today} to {end_date}")
                    st.rerun()  # Refresh to show the table
                else:
                    st.info("No valid bookings found for the next 2 weeks from today")
                    st.session_state.bookings_table_visible = False
            else:
                st.info(f"No bookings scheduled from {today} to {end_date}")
                st.session_state.bookings_table_visible = False
        else:
            st.warning("Could not load data from database")
            st.session_state.bookings_table_visible = False
            
    except Exception as e:
        st.error(f"Error loading bookings: {e}")
        print(f"🚨 Detailed error: {e}")
        st.session_state.bookings_table_visible = False

# Show table if visible in session_state
if st.session_state.bookings_table_visible and st.session_state.bookings_data:
    data = st.session_state.bookings_data
    df = data['df'].copy()
    
    # Get electric booking IDs from environment variable (comma-separated)
    electric_str = os.getenv('ELECTRIC', '')
    electric_bookings = [b.strip() for b in electric_str.split(',') if b.strip()]
    
    # Add Electric Allowance column
    df['Allowance electric'] = df.apply(
        lambda row: row['Nº Nights'] * 4 if str(row['Booking ID']).strip() in electric_bookings else 'N/A',
        axis=1
    )
    
    
    # Custom table with integrated buttons using Streamlit native components
    st.markdown("""
        <style>
        .custom-table-container {
            background: white;
            border-radius: 4px;
            overflow: hidden;
            box-shadow: 0 1px 3px rgba(0,0,0,0.08);
            margin-bottom: 20px;
            border: 1px solid #e0e0e0;
        }
        .custom-table-header {
            color: #424242;
            padding: 12px 16px;
            font-weight: 500;
            font-size: 13px;
            letter-spacing: 0.3px;
            text-align: left;
            background: #f5f5f5;
            border-bottom: 1px solid #e0e0e0;
        }
        .custom-table-row {
            border-bottom: 1px solid #f0f0f0;
            transition: all 0.15s ease;
        }
        .custom-table-row:hover .custom-table-cell {
            background-color: #fafafa;
        }
        .custom-table-cell {
            padding: 12px 16px;
            font-size: 13px;
            color: #424242;
            transition: background-color 0.15s ease;
        }
        .row-checkout-soon .custom-table-cell {
            background-color: #ffebee !important;
        }
        .row-checkin-soon .custom-table-cell {
            background-color: #e8f5e9 !important;
        }
        .badge-nights {
            background-color: #f0f0f0;
            color: #616161;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
        }
        .booking-id {
            font-weight: 500;
            color: #616161;
        }
        div[data-testid="column"] {
            padding: 0 !important;
            gap: 0 !important;
        }
        div[data-testid="stHorizontalBlock"] {
            gap: 0 !important;
        }
        .stButton button {
            background: #f5f5f5;
            color: #424242;
            border: 1px solid #e0e0e0;
            padding: 6px 12px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: 500;
            transition: all 0.15s ease;
            width: 100%;
        }
        .stButton button:hover {
            background: #e0e0e0;
            border-color: #bdbdbd;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Container for table
    st.markdown('<div class="custom-table-container">', unsafe_allow_html=True)
    
    # Table header - using columns
    header_cols = st.columns([1.5, 2.5, 1.5, 1.5, 1, 1.2])
    header_labels = ["Booking ID", "Guest Name", "Check-In", "Check-Out", "Nights", "Details"]
    for col, label in zip(header_cols, header_labels):
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
            
            if days_until_checkout <= 2:
                row_class = "row-checkout-soon"
            elif (days_until_checkin <= 2) and (days_until_checkin >= 0):
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
                # Use data directly from the DataFrame row
                matching_event = {
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
                
                st.session_state["selected_event"] = matching_event
                st.session_state["show_modal"] = True
                st.rerun()
    
    # Close container
    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- Calendar ----------------
st.subheader("🗓️ Calendar with events (click an event)")

# Initialize calendar navigation state
if 'calendar_month' not in st.session_state:
    st.session_state.calendar_month = date.today().month
if 'calendar_year' not in st.session_state:
    st.session_state.calendar_year = date.today().year

# Calendar navigation controls
nav_col1, nav_col2, nav_col3, nav_col4 = st.columns([2, 2, 1, 3])

with nav_col1:
    months = {
        1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
        5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
        9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
    }
    selected_month = st.selectbox(
        "Mes:",
        options=list(months.keys()),
        format_func=lambda x: months[x],
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
    st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)  # Spacer to align with selectbox
    if st.button("📅 Hoy", use_container_width=True):
        st.session_state.calendar_month = date.today().month
        st.session_state.calendar_year = date.today().year
        st.rerun()


def convert_db_to_events(cols, rows):
    """
    Converts DB data to the format required by FullCalendar
    Expected structure: ['ID', 'Booking ID', 'Check-In', 'Check-Out', 'Nombre,Apellidos', 
                          'Nº Noches', 'Nº Personas', 'Nº Adultos', 'Nº Niños', 'Nº Booking', 
                          'Status', 'Email', 'Movil', 'Comm y Cargos', 'Precio']
    """
    events = []
    
    # Get electric booking IDs from environment variable
    electric_str = os.getenv('ELECTRIC', '')
    electric_bookings = [b.strip() for b in electric_str.split(',') if b.strip()]
    
    # Create column mapping for easy access
    col_map = {col: idx for idx, col in enumerate(cols)}
    
    for row_idx, row in enumerate(rows):
        try:
            # Extract data using exact column names from your DB
            record_id = safe_convert_value(row[col_map.get('ID', 0)])
            booking_id = safe_convert_value(row[col_map.get('Booking ID', 1)])
            check_in_raw = row[col_map.get('Check-In', 2)]
            check_out_raw = row[col_map.get('Check-Out', 3)]
            guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos', 4)]) or "Guest without name"
            nights = safe_convert_value(row[col_map.get('Nº Noches', 5)])
            persons = safe_convert_value(row[col_map.get('Nº Personas', 6)])
            adults = safe_convert_value(row[col_map.get('Nº Adultos', 7)])
            children = safe_convert_value(row[col_map.get('Nº Niños', 8)])
            booking_number = safe_convert_value(row[col_map.get('Nº Booking', 9)])
            status = safe_convert_value(row[col_map.get('Status', 10)])
            email = safe_convert_value(row[col_map.get('Email', 11)])
            phone = safe_convert_value(row[col_map.get('Movil', 12)])
            charges = safe_convert_value(row[col_map.get('Comm y Cargos', 13)])
            price = safe_convert_value(row[col_map.get('Precio', 14)])
            
            # Convert dates if necessary
            if isinstance(check_in_raw, str):
                check_in = date.fromisoformat(check_in_raw)
            elif hasattr(check_in_raw, 'date'):  # datetime object
                check_in = check_in_raw.date()
            else:
                check_in = check_in_raw
                
            if isinstance(check_out_raw, str):
                check_out = date.fromisoformat(check_out_raw)
            elif hasattr(check_out_raw, 'date'):  # datetime object
                check_out = check_out_raw.date()
            else:
                check_out = check_out_raw
            
            # Skip cancelled bookings if within 3 days of check-in
            if status and status.lower() == 'cancelled' and (check_in - date.today()).days < 3:
                continue
            
            # Calculate electric allowance
            electric_allowance = nights * 4 if str(booking_id).strip() in electric_bookings else 'N/A'
            
            # Create descriptive title for the event
            title = f"{booking_id} - {guest_name}"
            
            # Create event for FullCalendar
            event = {
                "id": f"booking-{record_id}",
                "title": title,
                "start": check_in.isoformat() if check_in else date.today().isoformat(),
                "end": check_out.isoformat() if check_out else (date.today() + timedelta(days=1)).isoformat(),
                "allDay": True,
                "classNames": ["reserva"] + (["cancelled"] if status and status.lower() == 'cancelled' else []),
                "extendedProps": {
                    # Main data
                    "record_id": record_id,
                    "booking_id": booking_id,
                    "booking_number": booking_number,
                    "guest_name": guest_name,
                    "check_in": check_in.isoformat() if check_in else None,
                    "check_out": check_out.isoformat() if check_out else None,
                    "status": status,
                    
                    # Stay information
                    "nights": nights,
                    "persons": persons,
                    "adults": adults,
                    "children": children,
                    
                    # Contact
                    "email": email,
                    "phone": phone,
                    
                    # Financial (already converted by safe_convert_value)
                    "price": price,
                    "charges": charges,
                    "electric_allowance": electric_allowance,
                    
                    # Meta
                    "source": "database"
                }
            }
            
            events.append(event)
            
        except Exception as e:
            print(f"⚠️ Error processing row {row_idx}: {e}")
            print(f"   Row data: {row}")
            print(f"   Data types: {[type(val) for val in row]}")
            continue
    
    return events

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

# ✅✅✅ MINIMAL ADJUSTMENT: MAKE END INCLUSIVE
def _is_date_only(iso_str: str) -> bool:
    return isinstance(iso_str, str) and "T" not in iso_str  # YYYY-MM-DD format

_events_fixed = []
for ev in events:
    e = ev.copy()
    end_str = e.get("end")
    if end_str and _is_date_only(end_str):
        end_date = date.fromisoformat(end_str)
        e["end"] = end_date.isoformat()
        e["allDay"] = True
    _events_fixed.append(e)

# ---------------- Get screen width BEFORE calendar ----------------
viewport_width = st_javascript("window.innerWidth", key="viewport_width")
viewport_height = st_javascript("window.innerHeight", key="viewport_height")

# Calculate initial date for calendar based on selected month/year
initial_date = date(st.session_state.calendar_year, st.session_state.calendar_month, 1).isoformat()

# ---------------- Options ----------------
options = {
    "initialView": "dayGridMonth",
    "initialDate": initial_date,  # Set the calendar to the selected month/year
    "locale": "es",
    "firstDay": 1,
    "headerToolbar": {
        "left": "prev,next",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,timeGridDay,listWeek"
    },
    "height": 750,
    "weekNumbers": True,
    "selectable": True,
    "navLinks": True,
}

# Print viewport debug only once
if viewport_width and 'viewport_debug' not in st.session_state:
    st.session_state.viewport_debug = True
    print(f"🔍 Debug viewport: {viewport_width*0.3/7}")

# ---------------- Base CSS (with dynamic variables) ----------------
if viewport_width:
    # Calculate correct offset
    cell_offset = (viewport_width / 7) / 1.8  # Half cell based on 70% of viewport
    
    # Print viewport calculation only once
    if 'viewport_calculated' not in st.session_state:
        st.session_state.viewport_calculated = True
        print(f"✅ Calculated offset: {cell_offset:.1f}px for viewport of {viewport_width}px")
    
    custom_css = f"""
:root{{
  --viewport-width: {viewport_width}px;
  --res-bg: rgba(174, 249, 251, 0.8);
  --res-start: #15803d;
  --res-end: #dc2626;
}}
.fc .reserva .fc-event-main{{
  background-color: #DEEDFF !important;
  border: 0 !important;
  color: #000;
  font-weight: 700;
  text-align: center;
  filter: none !important;
  backdrop-filter: none !important;
}}
.fc .reserva{{
  background: none !important;
  filter: none !important;
  position: relative !important;
  border-radius: 4px !important;
}}

/* FIRST DAY of event - starts from the middle */
.fc .reserva.fc-event-start{{
  border-left: 25px solid var(--res-start) !important;
  transform: translateX({cell_offset:.1f}px) !important;
  position: relative !important;
}}

/* EVENT CONTINUATIONS (following weeks) - start from the beginning */
.fc .reserva:not(.fc-event-start){{
  transform: translateX(0px) !important;
  border-left: none !important;
}}

/* LAST DAY of event */
.fc .reserva.fc-event-end{{
  border-right: 10px solid var(--res-end) !important;
}}

/* LAST DAY of multi-week event - extends beyond the cell */
.fc .reserva.fc-event-end:not(.fc-event-start){{
  width: calc(100% + {cell_offset:.1f}px) !important;
  position: relative !important;
}}

.fc .reserva.fc-event-start::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 10px;
  background-color: #16a34a;
  border-radius: 2px;
  z-index: 999;
}}
.fc .reserva.fc-event-end::after {{
  content: "";
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 10px;
  background-color: #dc2626;
  border-radius: 2px;
  z-index: 999;
}}
.fc .cancelled .fc-event-main {{
  text-decoration: line-through !important;
  opacity: 0.6 !important;
  background-color: #FFE0E0 !important;
}}
"""
else:
    # CSS fallback without dynamic variables
    fallback_offset = (1200 * 0.7 / 7) / 2  # Half cell for 1200px viewport
    
    # Print fallback message only once
    if 'fallback_calculated' not in st.session_state:
        st.session_state.fallback_calculated = True
        print(f"⚠️ Using fallback offset: {fallback_offset:.1f}px")
    
    custom_css = f"""
:root{{
  --viewport-width: 1200px;
  --res-bg: rgba(174, 249, 251, 0.8);
  --res-start: #15803d;
  --res-end: #dc2626;
}}
.fc .reserva .fc-event-main{{
  background-color: #DEEDFF !important;
  border: 0 !important;
  color: #000;
  font-weight: 700;
  text-align: center;
  filter: none !important;
  backdrop-filter: none !important;
}}
.fc .reserva{{
  background: none !important;
  filter: none !important;
  position: relative !important;
  border-radius: 4px !important;
}}

/* FIRST DAY of event - starts from the middle */
.fc .reserva.fc-event-start{{
  border-left: 25px solid var(--res-start) !important;
  transform: translateX({fallback_offset:.1f}px) !important;
  position: relative !important;
}}

/* EVENT CONTINUATIONS (following weeks) - start from the beginning */
.fc .reserva:not(.fc-event-start){{
  transform: translateX(0px) !important;
  border-left: none !important;
}}

/* LAST DAY of event */
.fc .reserva.fc-event-end{{
  border-right: 10px solid var(--res-end) !important;
}}

/* LAST DAY of multi-week event - extends beyond the cell */
.fc .reserva.fc-event-end:not(.fc-event-start){{
  width: calc(100% + {fallback_offset:.1f}px) !important;
  position: relative !important;
}}

.fc .reserva.fc-event-start::before {{
  content: "";
  position: absolute;
  left: 0;
  top: 0;
  bottom: 0;
  width: 10px;
  background-color: #16a34a;
  border-radius: 2px;
  z-index: 999;
}}
.fc .reserva.fc-event-end::after {{
  content: "";
  position: absolute;
  right: 0;
  top: 0;
  bottom: 0;
  width: 10px;
  background-color: #dc2626;
  border-radius: 2px;
  z-index: 999;
}}
.fc .cancelled .fc-event-main {{
  text-decoration: line-through !important;
  opacity: 0.6 !important;
  background-color: #FFE0E0 !important;
}}
"""

# ---------------- Calendar ----------------
# Use dynamic key to force re-render when month/year changes
calendar_key = f"cal_{st.session_state.calendar_year}_{st.session_state.calendar_month}"
returned = calendar(events=_events_fixed, options=options, key=calendar_key, custom_css=custom_css)


# ----------- Capture clicks -----------  
clicked = None
if isinstance(returned, dict):
    if "eventClick" in returned and isinstance(returned["eventClick"], dict):
        clicked = returned["eventClick"].get("event")
    if not clicked and "clickedEvent" in returned:
        clicked = returned["clickedEvent"]

def _click_token(ev: dict) -> str:
    if not isinstance(ev, dict):
        return ""
    return f"{ev.get('id','')}|{ev.get('start','')}|{ev.get('end','')}"

if clicked:
    token = _click_token(clicked)
    if token and token != st.session_state.get("last_click_token"):
        st.session_state["last_click_token"] = token
        st.session_state["selected_event"] = clicked
        st.session_state["show_modal"] = True
    clicked = None

# ---------------- Modal ----------------
def _render_event_detail(ev: dict):
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
        status_emoji = "✅" if status == "Confirmed" else "⏳" if status == "Pending" else "📋"
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
        status_color = "#28a745" if status == "Confirmed" else "#ffc107" if status == "Pending" else "#6c757d"
        st.markdown(f'<span style="background-color: {status_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; font-weight: bold;">{status}</span>', unsafe_allow_html=True)
    
    st.divider()
    
    # VIEW MODE
    if not st.session_state.edit_mode:
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
            
            # Format monetary values with € symbol
            price_display = f"{price} €" if price != 'N/A' and price is not None else 'N/A'
            charges_display = f"{charges} €" if charges != 'N/A' and charges is not None else 'N/A'
            electric_display = f"{electric_allowance} €" if electric_allowance != 'N/A' and electric_allowance is not None else 'N/A'
            
            st.markdown(f"**Price:** {price_display}")
            st.markdown(f"**Comm & Charges:** {charges_display}")
            st.markdown(f"**Electric Allowance:** {electric_display}")
        
        # Contact information in separate section
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
                # Clean phone number and create WhatsApp link
                phone_clean = str(phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
                whatsapp_link = f"https://wa.me/{phone_clean}"
                st.markdown(f"**Mobile:** [📱 {phone}]({whatsapp_link})")
            else:
                st.markdown("**Mobile:** Not available")
    
    # EDIT MODE
    else:
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
                status_options = ["Confirmed", "Pending", "Cancelled"]
                try:
                    status_index = status_options.index(current_status)
                except:
                    status_index = 0
                new_status = st.selectbox("Status*", status_options, index=status_index)
                
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
                        conn = get_connection()
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
                        from services.bbdd_query import fetch_table
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
    
    # # Debug info in expander
    # with st.expander("🔧 Technical information (debug)"):
    #     st.markdown("**Complete event data:**")
    #     st.json(ev)

_has_dialog = hasattr(st, "dialog")

if st.session_state.get("show_modal") and st.session_state.get("selected_event") and _has_dialog:
    @st.dialog("Event Details", width="large")
    def _show_event_dialog():
        _render_event_detail(st.session_state["selected_event"])
        if not st.session_state.get('edit_mode', False):
            st.divider()
            if st.button("Close", use_container_width=True):
                st.session_state["show_modal"] = False
                st.session_state.edit_mode = False
                st.rerun()
    _show_event_dialog()
elif st.session_state.get("selected_event") and not _has_dialog:
    st.warning("Your Streamlit version doesn't support `st.dialog`. Showing detail inline.")
    _render_event_detail(st.session_state["selected_event"])

