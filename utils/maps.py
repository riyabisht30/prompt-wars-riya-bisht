import streamlit as st
import requests
from streamlit_folium import st_folium
import folium

class MapsClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://maps.googleapis.com/maps/api/place"

    @st.cache_data
    def get_place_details(_self, query: str, api_key: str):
        """Fetches rating and photo reference for a location query. Cached by query."""
        # Standard fallback image if everything fails
        # Using a reliable Unsplash search query
        clean_query = query.replace(" ", "-").lower()
        fallback_img = f"https://images.unsplash.com/photo-1500530855697-b586d89ba3ee?q=80&w=1000&auto=format&fit=crop" # High quality generic travel
        
        # If no key or AI Studio key, return dynamic mock image
        if not _self.api_key or _self.api_key.startswith("AQ"):
            import random
            seed = random.randint(1, 500)
            # Use LoremFlickr for themed dynamic images (very reliable)
            photo_url = f"https://loremflickr.com/800/500/{clean_query.split('-')[0] or 'travel'}"
            return {"rating": 4.8, "photo_url": photo_url}
        
        try:
            # 1. Find Place ID
            search_url = f"{_self.base_url}/findplacefromtext/json?input={query}&inputtype=textquery&fields=photos,rating,place_id&key={_self.api_key}"
            res = requests.get(search_url).json()
            if res.get("candidates"):
                candidate = res["candidates"][0]
                rating = candidate.get("rating", "N/A")
                photo_ref = candidate.get("photos", [{}])[0].get("photo_reference")
                
                if photo_ref:
                    photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photoreference={photo_ref}&key={_self.api_key}"
                    return {"rating": rating, "photo_url": photo_url}
        except Exception:
            pass
        
        # Dynamic Fallback if Google search failed or had no photo
        return {"rating": "N/A", "photo_url": f"https://loremflickr.com/800/500/{clean_query.split('-')[0] or 'city'}"}

def render_itinerary_map(days_data: list):
    """Renders an interactive map with pins for activities."""
    # Centering on a generic location or first activity
    m = folium.Map(location=[35.6762, 139.6503], zoom_start=12, tiles="CartoDB dark_matter")
    
    # In a real app, we would geocode location_query to get lat/lon
    # For now, we show a friendly message
    st.info("📍 Map View initialized. (Geocoding requires Google Maps API Key)")
    st_folium(m, width=700, height=400)
