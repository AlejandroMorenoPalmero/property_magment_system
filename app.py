# app.py
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from streamlit_calendar import calendar
from streamlit_javascript import st_javascript
from services.BBDD_query import fetch_table
from services.BBDD_conection import get_connection
import mysql.connector
from decimal import Decimal

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
    
    print("Columns:", cols)
    print("Bookings:")
    for row in rows:
        print(row)


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
st.subheader("📋 Bookings 2 weeks")

# Auto-load bookings data if not already loaded
if st.session_state.bookings_table_visible and st.session_state.bookings_data is None:
    # Calculate date range (from today for next 2 weeks)
    today = date.today()
    end_date = today + timedelta(days=14)  # From today + 2 weeks
    
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
                        booking_id = safe_convert_value(row[col_map.get('Booking ID')])
                        guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos')]) or "No name"
                        check_in = row[col_map.get('Check-In')]
                        check_out = row[col_map.get('Check-Out')]
                        nights = safe_convert_value(row[col_map.get('Nº Noches')])
                        
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
                            "Booking ID": booking_id,
                            "Name and Surname": guest_name,
                            "Check-In": check_in_display,
                            "Check-Out": check_out_display,
                            "Nº Nights": nights
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
    cargar = st.button("Refresh bookings", use_container_width=True)  # Changed text to "Refresh"
    
with colB:
    if st.session_state.bookings_table_visible:
        if st.button("Hide table"):
            st.session_state.bookings_table_visible = False
            st.session_state.bookings_data = None
            st.rerun()

if cargar:
    try:
        # Calculate date range (from today for next 2 weeks)
        today = date.today()
        end_date = today + timedelta(days=14)  # From today + 2 weeks
        
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
                        booking_id = safe_convert_value(row[col_map.get('Booking ID')])
                        guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos')]) or "No name"
                        check_in = row[col_map.get('Check-In')]
                        check_out = row[col_map.get('Check-Out')]
                        nights = safe_convert_value(row[col_map.get('Nº Noches')])
                        
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
                            "Booking ID": booking_id,
                            "Name and Surname": guest_name,
                            "Check-In": check_in_display,
                            "Check-Out": check_out_display,
                            "Nº Nights": nights
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
    
    # Apply conditional styling for check-ins and check-outs within 2 days
    def highlight_dates_soon(row):
        try:
            checkout_str = row['Check-Out']
            checkin_str = row['Check-In']
            
            # Process check-out date
            if isinstance(checkout_str, str):
                checkout_date = date.fromisoformat(checkout_str)
            else:
                checkout_date = checkout_str
                
            # Process check-in date
            if isinstance(checkin_str, str):
                checkin_date = date.fromisoformat(checkin_str)
            else:
                checkin_date = checkin_str
            
            days_until_checkout = (checkout_date - date.today()).days
            days_until_checkin = (checkin_date - date.today()).days
            
            # Priority: Check-out takes precedence over check-in for styling
            # If check-out is within 2 days or less (including today and past dates)
            if days_until_checkout <= 2:
                return ['background-color: #ffebee'] * len(row)  # Light red background
            # If check-in is within 2 days or less (including today and past dates)
            elif (days_until_checkin <= 2) and (days_until_checkin >= 0):
                return ['background-color: #e8f5e8'] * len(row)  # Light green background
            else:
                return [''] * len(row)
        except:
            return [''] * len(row)
    
    # Apply the styling
    styled_df = df.style.apply(highlight_dates_soon, axis=1)
    
    st.dataframe(styled_df, use_container_width=True, hide_index=True)

# ---------------- Calendar ----------------
st.subheader("🗓️ Calendar with events (click an event)")

def convert_db_to_events(cols, rows):
    """
    Converts DB data to the format required by FullCalendar
    Expected structure: ['ID', 'Booking ID', 'Check-In', 'Check-Out', 'Nombre,Apellidos', 
                          'Nº Noches', 'Nº Personas', 'Nº Adultos', 'Nº Niños', 'Nº Booking', 
                          'Status', 'Email', 'Movil', 'Comm y Cargos', 'Precio']
    """
    events = []
    
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
            
            # Create descriptive title for the event
            title = f"{guest_name}"
            if status:
                title += f" ({status})"
            
            # Create event for FullCalendar
            event = {
                "id": f"booking-{record_id}",
                "title": title,
                "start": check_in.isoformat() if check_in else date.today().isoformat(),
                "end": check_out.isoformat() if check_out else (date.today() + timedelta(days=1)).isoformat(),
                "allDay": True,
                "classNames": ["reserva"],
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

# ---------------- Options ----------------
options = {
    "initialView": "dayGridMonth",
    "locale": "es",
    "firstDay": 1,
    "headerToolbar": {
        "left": "prev,next today",
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
"""

# ---------------- Calendar ----------------
returned = calendar(events=_events_fixed, options=options, key="cal1", custom_css=custom_css)


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
    
    # Main title with status
    guest_name = ext.get('guest_name', 'Unknown guest')
    status = ext.get('status', '')
    status_emoji = "✅" if status == "Confirmed" else "⏳" if status == "Pending" else "📋"
    
    st.markdown(f"### {status_emoji} {guest_name}")
    if status:
        # Use compatible alternative with older Streamlit versions
        status_color = "#28a745" if status == "Confirmed" else "#ffc107" if status == "Pending" else "#6c757d"
        st.markdown(f'<span style="background-color: {status_color}; color: white; padding: 0.25rem 0.5rem; border-radius: 0.25rem; font-size: 0.875rem; font-weight: bold;">{status}</span>', unsafe_allow_html=True)
    
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
        st.markdown(f"**Price:** {price}")
        st.markdown(f"**Comm & Charges:** {charges}")
    
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
            st.markdown(f"**Mobile:** [{phone}](tel:{phone})")
        else:
            st.markdown("**Mobile:** Not available")
    
    # # Debug info in expander
    # with st.expander("🔧 Technical information (debug)"):
    #     st.markdown("**Complete event data:**")
    #     st.json(ev)

_has_dialog = hasattr(st, "dialog")

if st.session_state.get("show_modal") and st.session_state.get("selected_event") and _has_dialog:
    @st.dialog("Event Details", width="large")
    def _show_event_dialog():
        _render_event_detail(st.session_state["selected_event"])
        st.divider()
        if st.button("Close", use_container_width=True):
            st.session_state["show_modal"] = False
            st.rerun()
    _show_event_dialog()
elif st.session_state.get("selected_event") and not _has_dialog:
    st.warning("Your Streamlit version doesn't support `st.dialog`. Showing detail inline.")
    _render_event_detail(st.session_state["selected_event"])
