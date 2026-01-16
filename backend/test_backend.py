#!/usr/bin/env python3
"""
Test script to verify backend API functionality.
Run this after starting the backend to ensure everything works.
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.database.connection import get_connection
from backend.repositories.booking_repository import BookingRepository
from backend.services.booking_service import BookingService
from datetime import date, timedelta


def test_database_connection():
    """Test database connection."""
    print("🔍 Testing database connection...")
    try:
        conn = get_connection()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False


def test_repository():
    """Test repository functionality."""
    print("\n🔍 Testing repository...")
    try:
        repo = BookingRepository()
        bookings = repo.get_all(limit=5)
        print(f"✅ Repository working - fetched {len(bookings)} bookings")
        if bookings:
            print(f"   Sample booking: {bookings[0].booking_id} - {bookings[0].guest_name}")
        return True
    except Exception as e:
        print(f"❌ Repository test failed: {e}")
        return False


def test_service():
    """Test service functionality."""
    print("\n🔍 Testing service...")
    try:
        service = BookingService()
        
        # Test get all
        all_bookings = service.get_all_bookings(limit=3)
        print(f"✅ Service.get_all_bookings() - returned {len(all_bookings)} bookings")
        
        # Test get for period
        period_bookings = service.get_bookings_for_period(days=14)
        print(f"✅ Service.get_bookings_for_period() - returned {len(period_bookings)} bookings")
        
        # Test calendar events
        events = service.get_calendar_events(days=30)
        print(f"✅ Service.get_calendar_events() - returned {len(events)} events")
        
        # Test active bookings
        active = service.get_active_bookings()
        print(f"✅ Service.get_active_bookings() - returned {len(active)} active bookings")
        
        return True
    except Exception as e:
        print(f"❌ Service test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_models():
    """Test Pydantic models."""
    print("\n🔍 Testing models...")
    try:
        from backend.models.booking import BookingCreate, Booking
        
        # Create a booking
        booking_data = BookingCreate(
            booking_id="TEST-001",
            guest_name="Test Guest",
            check_in=date.today(),
            check_out=date.today() + timedelta(days=3),
            nights=3,
            status="Confirmed",
            persons=2,
            adults=2,
            children=0,
            price=300.0,
            charges=30.0
        )
        
        print(f"✅ Model validation successful")
        print(f"   Created test booking: {booking_data.booking_id}")
        return True
    except Exception as e:
        print(f"❌ Model test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("=" * 50)
    print("🧪 BACKEND API TESTS")
    print("=" * 50)
    
    results = {
        "Database Connection": test_database_connection(),
        "Pydantic Models": test_models(),
        "Repository Layer": test_repository(),
        "Service Layer": test_service()
    }
    
    print("\n" + "=" * 50)
    print("📊 TEST RESULTS")
    print("=" * 50)
    
    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<40} {status}")
    
    all_passed = all(results.values())
    print("=" * 50)
    
    if all_passed:
        print("🎉 All tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Check errors above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
