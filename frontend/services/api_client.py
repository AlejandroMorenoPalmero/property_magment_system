"""
API client for communicating with the backend.
"""

import os
from typing import List, Optional, Dict, Any
from datetime import date
import httpx
from dotenv import load_dotenv

load_dotenv()


class APIClient:
    """Client for making requests to the backend API."""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 30):
        """
        Initialize API client.
        
        Args:
            base_url: Base URL for the API (defaults to env variable or localhost)
            timeout: Request timeout in seconds
        """
        # Use BACKEND_URL from environment (set in docker-compose.yml)
        backend_url = os.getenv("BACKEND_URL", "http://localhost:8000")
        self.base_url = base_url or f"{backend_url}/api/v1"
        self.timeout = timeout
        self.client = httpx.Client(base_url=self.base_url, timeout=self.timeout)
    
    def _handle_response(self, response: httpx.Response) -> Any:
        """Handle API response and raise exceptions if needed."""
        try:
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get("detail", str(e))
            raise Exception(f"API Error ({e.response.status_code}): {error_detail}")
        except Exception as e:
            raise Exception(f"Request failed: {str(e)}")
    
    # Booking endpoints
    
    def get_bookings(
        self, 
        limit: Optional[int] = None,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        days: Optional[int] = None
    ) -> List[Dict]:
        """
        Get bookings with optional filters.
        
        Args:
            limit: Maximum number of results
            start_date: Start date for filtering
            end_date: End date for filtering
            days: Number of days from start_date
            
        Returns:
            List of booking dictionaries
        """
        params = {}
        if limit:
            params["limit"] = limit
        if start_date:
            params["start_date"] = start_date.isoformat()
        if end_date:
            params["end_date"] = end_date.isoformat()
        if days:
            params["days"] = days
        
        response = self.client.get("/bookings/", params=params)
        return self._handle_response(response)
    
    def get_booking(self, record_id: int) -> Dict:
        """
        Get a specific booking by ID.
        
        Args:
            record_id: Database record ID
            
        Returns:
            Booking dictionary
        """
        response = self.client.get(f"/bookings/{record_id}")
        return self._handle_response(response)
    
    def get_active_bookings(self) -> List[Dict]:
        """Get currently active bookings."""
        response = self.client.get("/bookings/active")
        return self._handle_response(response)
    
    def get_upcoming_checkins(self, days: int = 7) -> List[Dict]:
        """Get bookings with upcoming check-ins."""
        response = self.client.get("/bookings/upcoming-checkins", params={"days": days})
        return self._handle_response(response)
    
    def get_upcoming_checkouts(self, days: int = 7) -> List[Dict]:
        """Get bookings with upcoming check-outs."""
        response = self.client.get("/bookings/upcoming-checkouts", params={"days": days})
        return self._handle_response(response)
    
    def get_calendar_events(
        self, 
        start_date: Optional[date] = None, 
        days: int = 90
    ) -> List[Dict]:
        """Get bookings formatted as calendar events."""
        params = {"days": days}
        if start_date:
            params["start_date"] = start_date.isoformat()
        
        response = self.client.get("/bookings/calendar-events", params=params)
        return self._handle_response(response)
    
    def create_booking(self, booking_data: Dict) -> Dict:
        """
        Create a new booking.
        
        Args:
            booking_data: Booking data dictionary
            
        Returns:
            Created booking dictionary
        """
        response = self.client.post("/bookings/", json=booking_data)
        return self._handle_response(response)
    
    def update_booking(self, record_id: int, booking_data: Dict) -> Dict:
        """
        Update an existing booking.
        
        Args:
            record_id: Database record ID
            booking_data: Fields to update
            
        Returns:
            Updated booking dictionary
        """
        response = self.client.put(f"/bookings/{record_id}", json=booking_data)
        return self._handle_response(response)
    
    def delete_booking(self, record_id: int) -> None:
        """
        Delete a booking.
        
        Args:
            record_id: Database record ID
        """
        response = self.client.delete(f"/bookings/{record_id}")
        if response.status_code != 204:
            self._handle_response(response)
    
    def close(self):
        """Close the HTTP client."""
        self.client.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


# Singleton instance for easy import
api_client = APIClient()
