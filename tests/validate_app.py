import sys
import os

# Add root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.engine import TravelEngine

def test_engine_mock():
    print("Testing TravelEngine in Mock Mode...")
    engine = TravelEngine(api_key="mock_key", mock_mode=True)
    prefs = {
        "destination": "Paris",
        "days": 3,
        "budget": "Comfort",
        "pace": "Balanced",
        "interests": ["Food", "Art"]
    }
    itin = engine.generate_itinerary(prefs)
    assert "trip_title" in itin
    assert len(itin["days"]) > 0
    print("Passed: Mock Engine Test!")

if __name__ == "__main__":
    try:
        test_engine_mock()
        print("\nAll tests passed successfully!")
    except Exception as e:
        print(f"\nFailed: Test failed: {str(e)}")
        sys.exit(1)
