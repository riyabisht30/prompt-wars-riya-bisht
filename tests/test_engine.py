import pytest
from core.engine import TravelEngine

def test_mock_itinerary_generation():
    engine = TravelEngine(api_key="fake_key", mock_mode=True)
    prefs = {
        "destination": "Paris",
        "days": 2,
        "budget": "Luxury",
        "pace": "Balanced",
        "interests": ["Art"]
    }
    itin = engine.generate_itinerary(prefs)
    
    assert "trip_title" in itin
    assert "days" in itin
    assert len(itin["days"]) == 1 # Mock mode only returns 1 day for now
    assert itin["days"][0]["slots"][0]["activity"] == "Local Cafe Visit"

def test_itinerary_adaptation_mock():
    engine = TravelEngine(api_key="fake_key", mock_mode=True)
    itin = {"summary": "Original summary", "days": []}
    adapted = engine.adapt_itinerary(itin, "It is raining")
    
    assert "ADAPTED: It is raining" in adapted["summary"]

def test_engine_initialization():
    engine = TravelEngine(api_key="fake_key", mock_mode=True)
    assert engine.mock_mode is True
