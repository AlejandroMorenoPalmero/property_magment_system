"""
Configuration settings for Property Manager application.

Centralized configuration for constants and settings.
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Database Configuration
DATABASE_CONFIG = {
    "table_name": "bookings"
}


# Booking Configuration
ELECTRIC_ALLOWANCE_PER_NIGHT = 4  # € per night
DEFAULT_DATE_RANGE_DAYS = 14  # Default to 2 weeks


# Calendar Configuration
CALENDAR_CONFIG = {
    "locale": "es",
    "first_day": 1,  # Monday
    "height": 750,
    "initial_view": "dayGridMonth",
}

CALENDAR_MONTHS_ES = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril",
    5: "Mayo", 6: "Junio", 7: "Julio", 8: "Agosto",
    9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}


# Electric Allowance Booking IDs
def get_electric_booking_ids():
    """
    Gets the list of booking IDs eligible for electric allowance.
    
    Returns:
        List of booking ID strings
    """
    electric_str = os.getenv('ELECTRIC', '')
    return [b.strip() for b in electric_str.split(',') if b.strip()]


# Status Configuration
STATUS_OPTIONS = ["Confirmed", "Pending", "Cancelled"]

STATUS_COLORS = {
    "Confirmed": "#28a745",
    "Pending": "#ffc107",
    "Cancelled": "#6c757d"
}

STATUS_EMOJIS = {
    "Confirmed": "✅",
    "Pending": "⏳",
    "Cancelled": "❌"
}


# Table Configuration
TABLE_COLUMNS = [
    "Record ID", "Booking ID", "Booking Number", "Name and Surname",
    "Check-In", "Check-Out", "Nº Nights", "Status",
    "Persons", "Adults", "Children", "Email", "Phone",
    "Price", "Charges", "Allowance electric"
]

TABLE_HEADER_LABELS = ["Booking ID", "Guest Name", "Check-In", "Check-Out", "Nights", "Details"]


# Date Range Configuration
DATE_RANGE_MODES = ["Next days", "Custom dates"]


# UI Configuration
APP_TITLE = "Property Manager"
APP_ICON = "🏠"
APP_VERSION = "0.0.1"


# Highlight Configuration (for table rows)
CHECKOUT_SOON_DAYS = 2  # Highlight checkouts within X days
CHECKIN_SOON_DAYS = 2   # Highlight checkins within X days
