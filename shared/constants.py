"""
Shared constants across the application.
"""

# Booking statuses
BOOKING_STATUS_CONFIRMED = "Confirmed"
BOOKING_STATUS_PENDING = "Pending"
BOOKING_STATUS_CANCELLED = "Cancelled"

BOOKING_STATUSES = [
    BOOKING_STATUS_CONFIRMED,
    BOOKING_STATUS_PENDING,
    BOOKING_STATUS_CANCELLED
]

# Date formats
DATE_FORMAT_ISO = "%Y-%m-%d"
DATE_FORMAT_DISPLAY = "%d/%m/%Y"

# Electric allowance
ELECTRIC_ALLOWANCE_PER_NIGHT = 4.0

# API configuration
DEFAULT_API_TIMEOUT = 30  # seconds
