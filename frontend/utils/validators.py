"""Funciones de validación"""
from datetime import date


def validate_booking_data(booking_id: str, guest_name: str, check_in: date, check_out: date) -> bool:
    """
    Valida datos básicos de una reserva
    """
    if not booking_id or not guest_name:
        return False
    if not check_in or not check_out:
        return False
    if check_out <= check_in:
        return False
    return True


def calculate_nights(check_in: date, check_out: date) -> int:
    """
    Calcula número de noches entre dos fechas
    """
    if check_out > check_in:
        return (check_out - check_in).days
    return 0
