"""
CSS styles for Property Manager application.

Centralized styles for tables, calendar, and other UI components.
"""


def get_table_styles() -> str:
    """
    Returns CSS styles for the bookings table.
    
    Returns:
        CSS string for table styling
    """
    return """
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
    """


def get_calendar_styles(viewport_width: int = None) -> str:
    """
    Returns dynamic CSS styles for the calendar component.
    
    Args:
        viewport_width: Width of the viewport in pixels (optional)
        
    Returns:
        CSS string for calendar styling with dynamic calculations
    """
    if viewport_width:
        # Calculate correct offset based on viewport
        cell_offset = (viewport_width / 7) / 1.8  # Half cell based on 70% of viewport
        
        return f"""
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
        # Fallback CSS for when viewport width is not available
        fallback_offset = (1200 * 0.7 / 7) / 2
        
        return f"""
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


# Status color mapping
STATUS_COLORS = {
    "Confirmed": "#28a745",
    "Pending": "#ffc107",
    "Cancelled": "#6c757d"
}
