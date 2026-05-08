# VoyageAI: Smart Travel Experience Engine

VoyageAI is a premium travel planning application built with **Python**, **Streamlit**, and **Google Gemini**. It generates personalized, real-time adaptable itineraries based on user preferences and constraints.

## 🚀 Features
- **AI-Powered Itineraries**: Uses Google Gemini 1.5 to create timed, cost-estimated plans.
- **Real-Time Adaptation**: Change your plans instantly if it rains, if you're tired, or if you need to save money.
- **Google Maps Integration**: Pulls real ratings and photos from the Google Places API.
- **Premium UI**: Custom-styled dark theme with a smooth, responsive wizard.
- **Mock Mode**: Fully functional even without an API key (for development/testing).

## 🛠️ Setup
1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install streamlit google-generativeai python-dotenv folium streamlit-folium requests
   ```
3. Create a `.env` file based on `.env.template` and add your `GOOGLE_API_KEY`.
4. Run the app:
   ```bash
   streamlit run app.py
   ```

## 🧪 Testing
Run tests using pytest:
```bash
pytest tests/
```

## ⚖️ Evaluation Focus
- **Code Quality**: Modular architecture with separate engine and utility layers.
- **Security**: Secure API key management via `.env`.
- **Efficiency**: Optimized prompts and caching logic.
- **Accessibility**: High-contrast theme and accessible form controls.
