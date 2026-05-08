import google.generativeai as genai
import json
import os

class TravelEngine:
    def __init__(self, api_key: str, mock_mode: bool = False):
        self.mock_mode = mock_mode
        if not mock_mode:
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-flash-latest')

    def generate_itinerary(self, preferences: dict) -> dict:
        """
        Generates a structured travel itinerary based on user preferences.
        Returns a JSON object.
        """
        if self.mock_mode:
            return self._get_mock_data(preferences)

        prompt = self._build_prompt(preferences)
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception as e:
            return {"error": f"Gemini API Error: {str(e)}"}

    def _build_prompt(self, p: dict) -> str:
        return f"""
        You are an expert travel concierge. Generate a high-quality travel itinerary.
        
        Destination: {p.get('destination')}
        Duration: {p.get('days')} days
        Budget Level: {p.get('budget')}
        Travel Pace: {p.get('pace')}
        Interests: {', '.join(p.get('interests', []))}
        
        Return ONLY a JSON object with this exact structure:
        {{
            "trip_title": "string",
            "summary": "string",
            "total_estimated_cost": "string",
            "days": [
                {{
                    "day_number": 1,
                    "slots": [
                        {{
                            "time": "Morning",
                            "activity": "string (e.g. Arrival & Transfer)",
                            "description": "string",
                            "estimated_cost": "string",
                            "location_query": "string (MUST be a specific searchable landmark, airport name, or restaurant name in the destination city. DO NOT use generic terms like 'Arrival' or 'Transfer' here.)"
                        }},
                        {{
                            "time": "Afternoon",
                            "activity": "string",
                            "description": "string",
                            "estimated_cost": "string",
                            "location_query": "string (e.g. 'Eiffel Tower' or 'Shibuya Crossing')"
                        }},
                        {{
                            "time": "Evening",
                            "activity": "string",
                            "description": "string",
                            "estimated_cost": "string",
                            "location_query": "string"
                        }}
                    ]
                }}
            ]
        }}
        
        CRITICAL: The 'location_query' field will be used for a Google Maps search. Ensure it is a specific place name that returns a photo. For airport transfers, use the name of the main international airport in that city.
        """

    def _get_mock_data(self, p: dict) -> dict:
        """Return fallback data for development/testing."""
        return {
            "trip_title": f"Mock Adventure in {p.get('destination', 'Wonderland')}",
            "summary": "This is a sample itinerary generated in Mock Mode.",
            "total_estimated_cost": "$500 - $800",
            "days": [
                {
                    "day_number": 1,
                    "slots": [
                        {
                            "time": "Morning",
                            "activity": "Local Cafe Visit",
                            "description": "Start your day with local coffee and pastries.",
                            "estimated_cost": "$15",
                            "location_query": f"best cafe in {p.get('destination')}"
                        },
                        {
                            "time": "Afternoon",
                            "activity": "City Park Walk",
                            "description": "Explore the main green space of the city.",
                            "estimated_cost": "Free",
                            "location_query": f"central park in {p.get('destination')}"
                        },
                        {
                            "time": "Evening",
                            "activity": "Fine Dining",
                            "description": "Enjoy a top-rated local restaurant.",
                            "estimated_cost": "$60",
                            "location_query": f"top restaurant in {p.get('destination')}"
                        }
                    ]
                }
            ]
        }

    def adapt_itinerary(self, current_itinerary: dict, constraint: str) -> dict:
        """Adapts an existing itinerary based on a new constraint."""
        if self.mock_mode:
            current_itinerary["summary"] = f"ADAPTED: {constraint}. {current_itinerary['summary']}"
            return current_itinerary

        prompt = f"""
        Modify this travel itinerary based on this new constraint: "{constraint}".
        Return the updated JSON. Focus on changing the affected time slots.
        
        Current Itinerary:
        {json.dumps(current_itinerary)}
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json",
                )
            )
            return json.loads(response.text)
        except Exception:
            return current_itinerary
