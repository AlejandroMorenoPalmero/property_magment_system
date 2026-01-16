"""
Data formatting utilities for Property Manager application.

Functions for formatting data for display in the UI.
"""


def format_monetary_value(value, currency: str = "€") -> str:
    """
    Formats monetary values with currency symbol.
    
    Args:
        value: Numeric value or 'N/A'
        currency: Currency symbol to append
        
    Returns:
        Formatted string with currency symbol
    """
    if value == 'N/A' or value is None:
        return 'N/A'
    return f"{value} {currency}"


def format_phone_for_whatsapp(phone: str) -> str:
    """
    Cleans and formats phone number for WhatsApp links.
    
    Args:
        phone: Phone number in any format
        
    Returns:
        Cleaned phone number (digits only)
    """
    if not phone:
        return ""
    
    # Remove all non-digit characters
    phone_clean = str(phone).replace(' ', '').replace('-', '').replace('(', '').replace(')', '').replace('+', '')
    return phone_clean


def click_token(ev: dict) -> str:
    """
    Generates unique token for event click tracking.
    
    Args:
        ev: Event dictionary
        
    Returns:
        Unique string token combining id, start, and end
    """
    if not isinstance(ev, dict):
        return ""
    return f"{ev.get('id','')}|{ev.get('start','')}|{ev.get('end','')}"
