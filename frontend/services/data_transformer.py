"""
Data transformation utilities for Property Manager application.

Functions for converting database data to different formats for UI components.
"""
import os
import pandas as pd
from datetime import date, timedelta
from ..utils.converters import safe_convert_value, convert_date_field


def convert_db_to_events(cols: list, rows: list) -> list:
    """
    Converts database data to the format required by FullCalendar.
    
    Args:
        cols: List of column names from database
        rows: List of row tuples from database
        
    Returns:
        List of event dictionaries formatted for FullCalendar
    """
    events = []
    
    # Get electric booking IDs from environment variable
    electric_str = os.getenv('ELECTRIC', '')
    electric_bookings = [b.strip() for b in electric_str.split(',') if b.strip()]
    
    # Create column mapping for easy access
    col_map = {col: idx for idx, col in enumerate(cols)}
    
    for row_idx, row in enumerate(rows):
        try:
            # Extract data using exact column names from DB
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
            
            # Convert dates
            check_in = convert_date_field(check_in_raw)
            check_out = convert_date_field(check_out_raw)
            
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
                    
                    # Financial
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
            continue
    
    return events


def convert_db_to_dataframe(cols: list, rows: list, start_date: date, end_date: date) -> pd.DataFrame:
    """
    Converts database data to a pandas DataFrame with filtering.
    
    Args:
        cols: List of column names from database
        rows: List of row tuples from database
        start_date: Filter start date
        end_date: Filter end date
        
    Returns:
        Filtered DataFrame with booking data
    """
    col_map = {col: idx for idx, col in enumerate(cols)}
    booking_data = []
    
    for row in rows:
        try:
            check_in_raw = row[col_map.get('Check-In')]
            check_out_raw = row[col_map.get('Check-Out')]
            
            # Convert dates
            check_in = convert_date_field(check_in_raw)
            check_out = convert_date_field(check_out_raw)
            
            # Filter logic: Include bookings that overlap with the period
            is_currently_active = check_in <= start_date <= check_out
            has_checkin_in_period = start_date <= check_in <= end_date
            has_checkout_in_period = start_date <= check_out <= end_date
            overlaps_period = check_in <= end_date and check_out >= start_date
            
            if not (is_currently_active or has_checkin_in_period or has_checkout_in_period or overlaps_period):
                continue
            
            # Extract all data from DB row
            record_id = safe_convert_value(row[col_map.get('ID')])
            booking_id = safe_convert_value(row[col_map.get('Booking ID')])
            guest_name = safe_convert_value(row[col_map.get('Nombre,Apellidos')]) or "No name"
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
            elif hasattr(check_in, 'isoformat'):
                check_in_display = check_in.isoformat()
            else:
                check_in_display = str(check_in)
                
            if isinstance(check_out, str):
                check_out_display = check_out
            elif hasattr(check_out, 'isoformat'):
                check_out_display = check_out.isoformat()
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
        return pd.DataFrame(booking_data)
    else:
        return pd.DataFrame()


def add_electric_allowance(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds electric allowance column to bookings DataFrame.
    
    Args:
        df: DataFrame with booking data
        
    Returns:
        DataFrame with added 'Allowance electric' column
    """
    # Get electric booking IDs from environment variable
    electric_str = os.getenv('ELECTRIC', '')
    electric_bookings = [b.strip() for b in electric_str.split(',') if b.strip()]
    
    # Add Electric Allowance column
    df['Allowance electric'] = df.apply(
        lambda row: row['Nº Nights'] * 4 if str(row['Booking ID']).strip() in electric_bookings else 'N/A',
        axis=1
    )
    
    return df


def fix_calendar_events_dates(events: list) -> list:
    """
    Fixes date formats for calendar events to ensure proper display.
    Makes end dates inclusive for date-only events.
    
    Args:
        events: List of event dictionaries
        
    Returns:
        List of events with fixed date formats
    """
    from utils.converters import is_date_only
    
    fixed_events = []
    for ev in events:
        e = ev.copy()
        end_str = e.get("end")
        if end_str and is_date_only(end_str):
            end_date = date.fromisoformat(end_str)
            e["end"] = end_date.isoformat()
            e["allDay"] = True
        fixed_events.append(e)
    
    return fixed_events
