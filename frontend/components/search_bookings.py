"""
Search Bookings component for Property Manager application.

Advanced search functionality with multiple filters.
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
import sys
import os

# Add parent directory to access shared modules
parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, parent_dir)

from backend.database.connection import get_connection
from ..config import STATUS_OPTIONS
from ..utils.converters import safe_convert_value


def render_search_bookings_page():
    """
    Main page for searching and filtering bookings.
    """
    st.title("🔍 Search Bookings")
    st.caption("Find bookings using advanced filters")
    
    # Load all unique Booking IDs from database
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT `Booking ID` FROM bookings ORDER BY `Booking ID`")
        booking_ids = [row[0] for row in cursor.fetchall() if row[0]]
        cursor.close()
    except Exception as e:
        st.error(f"Error loading Booking IDs: {e}")
        booking_ids = []
    
    # Search filters section
    with st.expander("🔎 Search Filters", expanded=True):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("#### 📋 Booking Info")
            booking_id_filter = st.selectbox(
                "Booking ID",
                options=["All"] + booking_ids,
                index=0
            )
            guest_name_filter = st.text_input("Guest Name", placeholder="e.g., John Doe")
            booking_number_filter = st.text_input("Booking Number", placeholder="e.g., 123456789")
        
        with col2:
            st.markdown("#### 📅 Dates")
            date_filter_type = st.selectbox(
                "Date Filter Type",
                ["All Dates", "Check-In Range", "Check-Out Range", "Any Date Range"]
            )
            
            if date_filter_type == "Check-In Range":
                col_start, col_end = st.columns(2)
                with col_start:
                    check_in_start = st.date_input("Check-In From", value=date.today())
                with col_end:
                    check_in_end = st.date_input("Check-In To (optional)", value=None)
                
                check_out_start = None
                check_out_end = None
                date_range_start = None
                date_range_end = None
                
            elif date_filter_type == "Check-Out Range":
                col_start, col_end = st.columns(2)
                with col_start:
                    check_out_start = st.date_input("Check-Out From", value=date.today())
                with col_end:
                    check_out_end = st.date_input("Check-Out To (optional)", value=None)
                
                check_in_start = None
                check_in_end = None
                date_range_start = None
                date_range_end = None
                
            elif date_filter_type == "Any Date Range":
                col_start, col_end = st.columns(2)
                with col_start:
                    date_range_start = st.date_input("From Date", value=date.today())
                with col_end:
                    date_range_end = st.date_input("To Date", value=date.today())
                
                check_in_start = None
                check_in_end = None
                check_out_start = None
                check_out_end = None
                
            else:  # All Dates
                check_in_start = None
                check_in_end = None
                check_out_start = None
                check_out_end = None
                date_range_start = None
                date_range_end = None
        
        with col3:
            st.markdown("#### 📊 Status & Other")
            status_filter = st.multiselect(
                "Status",
                STATUS_OPTIONS,
                default=None,
                placeholder="All statuses"
            )
            
            min_nights = st.number_input("Min Nights", min_value=0, value=0)
            max_nights = st.number_input("Max Nights", min_value=0, value=0)
            
            email_filter = st.text_input("Email", placeholder="guest@example.com")
    
    # Search buttons
    col_search, col_reset = st.columns([1, 1])
    with col_search:
        search_button = st.button("🔍 Search", use_container_width=True, type="primary")
    with col_reset:
        reset_button = st.button("🔄 Reset Filters", use_container_width=True)
    
    # Reset filters
    if reset_button:
        st.rerun()
    
    # Perform search
    if search_button or 'search_results' in st.session_state:
        if search_button:
            try:
                conn = get_connection()
                cursor = conn.cursor()
                
                # Build dynamic query
                query = "SELECT * FROM bookings WHERE 1=1"
                params = []
                
                # Add filters
                if booking_id_filter and booking_id_filter != "All":
                    query += " AND `Booking ID` = %s"
                    params.append(booking_id_filter)
                
                if guest_name_filter:
                    query += " AND `Nombre,Apellidos` LIKE %s"
                    params.append(f"%{guest_name_filter}%")
                
                if booking_number_filter:
                    query += " AND `Nº Booking` LIKE %s"
                    params.append(f"%{booking_number_filter}%")
                
                # Check-In Range filter
                if check_in_start:
                    if check_in_end:
                        # Range specified
                        query += " AND `Check-In` >= %s AND `Check-In` <= %s"
                        params.append(check_in_start)
                        params.append(check_in_end)
                    else:
                        # Only start date - all check-ins from this date forward
                        query += " AND `Check-In` >= %s"
                        params.append(check_in_start)
                
                # Check-Out Range filter
                if check_out_start:
                    if check_out_end:
                        # Range specified
                        query += " AND `Check-Out` >= %s AND `Check-Out` <= %s"
                        params.append(check_out_start)
                        params.append(check_out_end)
                    else:
                        # Only start date - all check-outs from this date forward
                        query += " AND `Check-Out` >= %s"
                        params.append(check_out_start)
                
                # Any Date Range filter (overlapping bookings)
                if date_range_start and date_range_end:
                    query += " AND `Check-In` <= %s AND `Check-Out` >= %s"
                    params.append(date_range_end)
                    params.append(date_range_start)
                
                if status_filter:
                    placeholders = ','.join(['%s'] * len(status_filter))
                    query += f" AND `Status` IN ({placeholders})"
                    params.extend(status_filter)
                
                if min_nights > 0:
                    query += " AND `Nº Noches` >= %s"
                    params.append(min_nights)
                
                if max_nights > 0:
                    query += " AND `Nº Noches` <= %s"
                    params.append(max_nights)
                
                if email_filter:
                    query += " AND `Email` LIKE %s"
                    params.append(f"%{email_filter}%")
                
                # Order by most recent
                query += " ORDER BY `Check-In` DESC"
                
                # Execute query
                cursor.execute(query, params)
                results = cursor.fetchall()
                columns = [desc[0] for desc in cursor.description]
                
                cursor.close()
                
                # Store results in session state
                st.session_state.search_results = {
                    'columns': columns,
                    'rows': results,
                    'count': len(results)
                }
                
            except Exception as e:
                st.error(f"❌ Error searching: {e}")
                st.session_state.search_results = None
        
        # Display results
        if st.session_state.get('search_results'):
            results_data = st.session_state.search_results
            
            st.divider()
            st.subheader(f"📊 Search Results ({results_data['count']} bookings found)")
            
            if results_data['count'] > 0:
                # Convert to DataFrame
                col_map = {col: idx for idx, col in enumerate(results_data['columns'])}
                
                data_rows = []
                for row in results_data['rows']:
                    data_rows.append({
                        "ID": safe_convert_value(row[col_map.get('ID')]),
                        "Booking ID": safe_convert_value(row[col_map.get('Booking ID')]),
                        "Guest Name": safe_convert_value(row[col_map.get('Nombre,Apellidos')]),
                        "Check-In": safe_convert_value(row[col_map.get('Check-In')]),
                        "Check-Out": safe_convert_value(row[col_map.get('Check-Out')]),
                        "Nights": safe_convert_value(row[col_map.get('Nº Noches')]),
                        "Status": safe_convert_value(row[col_map.get('Status')]),
                        "Price": safe_convert_value(row[col_map.get('Precio')]),
                        "Email": safe_convert_value(row[col_map.get('Email')]),
                        "Phone": safe_convert_value(row[col_map.get('Movil')]),
                    })
                
                df = pd.DataFrame(data_rows)
                
                # Display options
                view_mode = st.radio(
                    "View Mode:",
                    ["Table View", "Card View", "Detailed List"],
                    horizontal=True
                )
                
                if view_mode == "Table View":
                    # Standard table view
                    st.dataframe(
                        df,
                        use_container_width=True,
                        hide_index=True,
                        column_config={
                            "Price": st.column_config.NumberColumn(
                                "Price",
                                format="%.2f €"
                            ),
                            "Status": st.column_config.TextColumn(
                                "Status",
                            ),
                        }
                    )
                    
                    # Download option
                    csv = df.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"bookings_search_{date.today()}.csv",
                        mime="text/csv",
                    )
                
                elif view_mode == "Card View":
                    # Card-based view
                    cols_per_row = 3
                    for i in range(0, len(data_rows), cols_per_row):
                        cols = st.columns(cols_per_row)
                        for j, col in enumerate(cols):
                            if i + j < len(data_rows):
                                row_data = data_rows[i + j]
                                with col:
                                    with st.container(border=True):
                                        st.markdown(f"### {row_data['Booking ID']}")
                                        st.markdown(f"**{row_data['Guest Name']}**")
                                        st.caption(f"Status: {row_data['Status']}")
                                        st.markdown(f"📅 {row_data['Check-In']} → {row_data['Check-Out']}")
                                        st.markdown(f"🌙 {row_data['Nights']} nights")
                                        st.markdown(f"💰 {row_data['Price']} €")
                                        if row_data['Email']:
                                            st.markdown(f"📧 {row_data['Email']}")
                
                else:  # Detailed List
                    # Detailed list view with expanders
                    for row_data in data_rows:
                        status_emoji = "✅" if row_data['Status'] == "Confirmed" else "⏳" if row_data['Status'] == "Pending" else "❌"
                        with st.expander(f"{status_emoji} {row_data['Booking ID']} - {row_data['Guest Name']}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**Booking Information**")
                                st.markdown(f"- Record ID: {row_data['ID']}")
                                st.markdown(f"- Booking ID: {row_data['Booking ID']}")
                                st.markdown(f"- Status: {row_data['Status']}")
                                st.markdown(f"- Guest: {row_data['Guest Name']}")
                            
                            with col2:
                                st.markdown("**Stay Details**")
                                st.markdown(f"- Check-In: {row_data['Check-In']}")
                                st.markdown(f"- Check-Out: {row_data['Check-Out']}")
                                st.markdown(f"- Nights: {row_data['Nights']}")
                                st.markdown(f"- Price: {row_data['Price']} €")
                            
                            if row_data['Email'] or row_data['Phone']:
                                st.markdown("**Contact**")
                                if row_data['Email']:
                                    st.markdown(f"- Email: {row_data['Email']}")
                                if row_data['Phone']:
                                    st.markdown(f"- Phone: {row_data['Phone']}")
                
                # Summary statistics
                st.divider()
                st.subheader("📈 Summary Statistics")
                
                stat_col1, stat_col2, stat_col3, stat_col4 = st.columns(4)
                
                with stat_col1:
                    st.metric("Total Bookings", results_data['count'])
                
                with stat_col2:
                    total_nights = df['Nights'].sum()
                    st.metric("Total Nights", f"{total_nights:,}")
                
                with stat_col3:
                    if 'Price' in df.columns and df['Price'].notna().any():
                        total_revenue = df['Price'].sum()
                        st.metric("Total Revenue", f"{total_revenue:,.2f} €")
                    else:
                        st.metric("Total Revenue", "N/A")
                
                with stat_col4:
                    if 'Price' in df.columns and df['Price'].notna().any():
                        avg_price = df['Price'].mean()
                        st.metric("Avg Price", f"{avg_price:.2f} €")
                    else:
                        st.metric("Avg Price", "N/A")
            
            else:
                st.info("🔍 No bookings found matching your search criteria. Try adjusting the filters.")
