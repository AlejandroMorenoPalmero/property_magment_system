"""
Shared constants across the application.
"""

import os
from dotenv import load_dotenv

load_dotenv()


def get_db_config():
    """Get database configuration from environment variables."""
    return {
        'host': os.getenv('MYSQL_HOST', 'localhost'),
        'port': int(os.getenv('MYSQL_PORT', 3306)),
        'user': os.getenv('MYSQL_USER', 'property_user'),
        'password': os.getenv('MYSQL_PASSWORD', 'property_pass'),
        'database': os.getenv('MYSQL_DATABASE', 'property_manager'),
        'charset': 'utf8mb4',
        'autocommit': False
    }


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
