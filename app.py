import streamlit as st
import os
from dotenv import load_dotenv

# --- IMPORTS ---
from core.engine import TravelEngine
from utils.maps import MapsClient, render_itinerary_map

# --- CACHED RESOURCES ---
@st.cache_resource
def get_engine(api_key: str):
    return TravelEngine(api_key=api_key, mock_mode=(not api_key))

@st.cache_resource
def get_maps_client(api_key: str):
    return MapsClient(api_key=api_key)

# --- CONFIGURATION LOADER ---
class Config:
    """Securely loads and validates environment variables."""
    def __init__(self):
        load_dotenv()
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        # Use a dedicated Maps key if available, otherwise fallback to the main key
        self.maps_api_key = os.getenv("GOOGLE_MAPS_API_KEY") or self.google_api_key
        
        # Load Hero Background
        self.hero_bg_base64 = ""
        try:
            import base64
            with open("assets/hero_bg.png", "rb") as image_file:
                self.hero_bg_base64 = base64.b64encode(image_file.read()).decode()
        except:
            pass

    def validate(self):
        if not self.google_api_key:
            st.warning("⚠️ No GOOGLE_API_KEY found (Gemini). Running in Mock Mode.")
        if not self.maps_api_key or self.maps_api_key.startswith("AQ"):
            st.info("ℹ️ Your current key looks like an AI Studio key. Google Maps/Places features require a standard Google Cloud GCP key.")

config = Config()

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="VoyageAI | Smart Travel Engine",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- SESSION STATE DEFAULTS ---
if "theme" not in st.session_state:
    st.session_state.theme = "light"
if "step" not in st.session_state:
    st.session_state.step = 0
if "trip_data" not in st.session_state:
    st.session_state.trip_data = {}
if "itinerary" not in st.session_state:
    st.session_state.itinerary = None
if "wishlist" not in st.session_state:
    st.session_state.wishlist = []
if "temp_budget" not in st.session_state:
    st.session_state.temp_budget = "Comfort"

# --- THEME PALETTES ---
THEMES = {
    "light": {
        "--bg":         "#F8F9FF",
        "--surface":    "#FFFFFF",
        "--accent":     "#5B4FF0",
        "--accent2":    "#FF6B9D",
        "--text":       "#1A1A2E",
        "--text-muted": "#6B7280",
        "--border":     "#E5E7EB",
        "--shadow":     "rgba(91,79,240,0.10)",
        "--hero-grad":  "linear-gradient(135deg, #5B4FF0 0%, #FF6B9D 100%)",
    },
    "dark": {
        "--bg":         "#0D0D1A",
        "--surface":    "#1A1A2E",
        "--accent":     "#7C6FF7",
        "--accent2":    "#FF8FB3",
        "--text":       "#F0F0FF",
        "--text-muted": "#9CA3AF",
        "--border":     "#2D2D45",
        "--shadow":     "rgba(124,111,247,0.15)",
        "--hero-grad":  "linear-gradient(135deg, #7C6FF7 0%, #FF8FB3 100%)",
    }
}

def inject_theme():
    """Inject CSS custom properties, fonts, and global styles."""
    t = THEMES[st.session_state.theme]
    # Add Hero BG to the variables
    bg_url = f"data:image/png;base64,{config.hero_bg_base64}" if config.hero_bg_base64 else ""
    vars_css = "\n".join([f"    {k}: {v};" for k, v in t.items()])
    vars_css += f"\n    --hero-bg: url({bg_url});"
    
    css_content = f"""
<link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap" rel="stylesheet">
<style>
:root {{
{vars_css}
}}
* {{ font-family: 'Plus Jakarta Sans', sans-serif !important; }}
.stApp {{ background-color: var(--bg) !important; color: var(--text) !important; }}

/* ─── HERO CONTAINER ─── */
.hero-container {{
    position: relative;
    background-image: linear-gradient(rgba(0,0,0,0.5), rgba(0,0,0,0.3)), var(--hero-bg);
    background-size: cover;
    background-position: center;
    border-radius: 30px;
    padding: 120px 20px;
    margin-bottom: 40px;
    overflow: hidden;
    box-shadow: 0 20px 50px var(--shadow);
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center !important;
    color: white !important;
}}
.hero-container * {{ color: white !important; text-align: center !important; }}
.hero-title {{
    font-size: 4rem;
    font-weight: 800;
    margin-bottom: 20px;
    line-height: 1.1;
}}
.hero-subtitle {{
    font-size: 1.3rem;
    max-width: 600px;
    margin: 0 auto 40px auto;
    opacity: 0.95;
    font-weight: 400;
    text-align: center;
}}
.voyage-logo {{ font-size: 1.4rem; font-weight: 800; background: var(--hero-grad); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }}
.stButton > button {{ background: var(--accent) !important; color: #fff !important; border: none !important; border-radius: 12px !important; font-weight: 700 !important; padding: 10px 22px !important; transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important; box-shadow: 0 4px 14px var(--shadow) !important; }}
.stButton > button:hover {{ transform: translateY(-2px) scale(1.05) !important; box-shadow: 0 8px 25px var(--shadow) !important; }}
@keyframes shimmer {{ 0% {{ background-position: -200% 0; }} 100% {{ background-position: 200% 0; }} }}
.shimmer-btn > button {{ background: linear-gradient(90deg, var(--accent), var(--accent2), var(--accent)) !important; background-size: 200% 100% !important; animation: shimmer 3s linear infinite !important; border-radius: 50px !important; padding: 15px 40px !important; font-size: 1.2rem !important; }}
.love-btn-active > button {{ background: #FF4757 !important; color: white !important; border-radius: 50% !important; width: 50px !important; height: 50px !important; }}
.love-btn-inactive > button {{ background: var(--bg) !important; color: var(--text-muted) !important; border-radius: 50% !important; width: 50px !important; height: 50px !important; border: 1px solid var(--border) !important; }}
.floating-wishlist {{ position: fixed; bottom: 30px; right: 30px; background: var(--hero-grad); color: white; padding: 15px 25px; border-radius: 50px; font-weight: 800; box-shadow: 0 8px 32px var(--shadow); z-index: 1000; }}
@keyframes heartPop {{ 0% {{ transform: scale(1); }} 50% {{ transform: scale(1.4); }} 100% {{ transform: scale(1); }} }}
.love-btn-active {{ animation: heartPop 0.45s ease; }}
@keyframes gradientFlow {{ 0% {{ background-position: 0% 50%; }} 50% {{ background-position: 100% 50%; }} 100% {{ background-position: 0% 50%; }} }}
.hero-title {{ font-size: 3.8rem; font-weight: 800; background: linear-gradient(-45deg, #5B4FF0, #FF6B9D, #00d4aa, #5B4FF0); background-size: 300% 300%; animation: gradientFlow 8s ease infinite; -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
@keyframes float {{ 0% {{ transform: translate(0, 0) rotate(0deg); opacity: 0; }} 10% {{ opacity: 0.5; }} 100% {{ transform: translate(100vw, -100vh) rotate(360deg); opacity: 0; }} }}
.floating-icon {{ position: fixed; font-size: 2rem; pointer-events: none; z-index: 0; animation: float 20s linear infinite; }}
.glass-card {{ background: rgba(255, 255, 255, 0.7); backdrop-filter: blur(12px); border: 1px solid rgba(255, 255, 255, 0.3); border-radius: 24px; padding: 40px; }}
[data-theme="dark"] .glass-card {{ background: rgba(26, 26, 46, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); }}
.day-header {{ position: sticky; top: 0; z-index: 10; background: var(--surface); padding: 15px 25px; border-left: 6px solid var(--accent); border-radius: 0 15px 15px 0; margin-bottom: 25px; }}
.time-slot-card {{ display: flex; background: var(--surface); border-radius: 18px; margin-bottom: 20px; overflow: hidden; box-shadow: 0 4px 20px var(--shadow); }}
.accent-morning {{ border-left: 8px solid #FF9F43; }}
.accent-afternoon {{ border-left: 8px solid #0984E3; }}
.accent-evening {{ border-left: 8px solid #6C5CE7; }}
.slot-image {{ width: 250px; height: 180px; object-fit: cover; }}
.slot-details {{ padding: 20px; flex: 1; }}
@media (max-width: 768px) {{ .time-slot-card {{ flex-direction: column; }} .slot-image {{ width: 100%; height: 200px; }} .hero-title {{ font-size: 2.5rem; }} }}
</style>
<div class="floating-icon" style="left: 10%; bottom: 10%; animation-delay: 0s;">✈️</div>
<div class="floating-icon" style="left: 30%; bottom: 20%; animation-delay: 5s;">🗺️</div>
<div class="floating-icon" style="left: 70%; bottom: 15%; animation-delay: 10s;">🌅</div>
"""
    st.markdown(css_content, unsafe_allow_html=True)

# Apply CSS
inject_theme()

def render_loader(text="Gemini is thinking..."):
    """Render a beautiful custom CSS loader."""
    st.markdown(f"""
        <div class="loader-card fade-in">
            <div class="spinner-ring"></div>
            <h3 style="margin:0; color:var(--accent);">✨ {text}</h3>
            <p style="color:var(--text-muted); margin-top:10px;">Crafting your perfect journey...</p>
        </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────
# NAVBAR
# ─────────────────────────────────────────
nav_left, nav_right = st.columns([2, 2])
with nav_left:
    st.markdown('<div class="voyage-logo">🌍 VoyageAI</div>', unsafe_allow_html=True)
with nav_right:
    r1, r2 = st.columns(2)
    with r1:
        if st.button("💖 Wishlist", use_container_width=True):
            st.session_state.step = 4
            st.rerun()
    with r2:
        toggle_label = "☀️ Light" if st.session_state.theme == "dark" else "🌙 Dark"
        if st.button(toggle_label, use_container_width=True):
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()

st.markdown("---")

# ─────────────────────────────────────────
# STEP 0 — HERO
# ─────────────────────────────────────────
if st.session_state.step == 0:
    st.markdown("""
        <div class="hero-container fade-in">
            <h1 class="hero-title">Experience Travel<br>Reimagined</h1>
            <p class="hero-subtitle">Smart itineraries powered by Google Gemini. Your dream journey starts with a single click.</p>
    """, unsafe_allow_html=True)
    
    col_cta = st.columns([1, 2, 1])[1]
    with col_cta:
        st.markdown('<div class="shimmer-btn">', unsafe_allow_html=True)
        if st.button("🚀 Start Planning", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# STEP 1 — DESTINATION & DATES
# ─────────────────────────────────────────
elif st.session_state.step == 1:
    st.markdown('<div class="fade-in"><div class="glass-card">', unsafe_allow_html=True)
    st.progress(33, text="Step 1 of 3 — Where and When?")
    st.markdown("## 📍 Destination & Dates")
    with st.form("step1"):
        dest = st.text_input("Destination", placeholder="e.g. Tokyo, Japan").strip()
        dates = st.date_input("Travel Dates", value=[])
        num_ppl = st.number_input("Travelers", min_value=1, value=1)
        if st.form_submit_button("Next →"):
            if dest and dates:
                st.session_state.trip_data.update({"destination": dest, "dates": dates, "people": num_ppl})
                st.session_state.step = 2
                st.rerun()
            else: st.error("Please provide both a destination and travel dates.")
    st.markdown('</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# STEP 2 — TRAVEL STYLE
# ─────────────────────────────────────────
elif st.session_state.step == 2:
    st.markdown('<div class="fade-in"><div class="glass-card">', unsafe_allow_html=True)
    st.progress(66, text="Step 2 of 3 — Your Travel Style")
    st.markdown("## 🎭 Your Travel Style")
    
    b_col1, b_col2, b_col3 = st.columns(3)
    budget_opts = {"Budget": ("🎒", "Keep it lean"), "Comfort": ("🛎️", "Balanced"), "Luxury": ("👑", "No limits")}
    for i, (n, (ic, de)) in enumerate(budget_opts.items()):
        with [b_col1, b_col2, b_col3][i]:
            sel = st.session_state.temp_budget == n
            st.markdown(f'<div style="text-align:center;padding:15px;border-radius:15px;background:var(--surface);border:2px solid {"var(--accent)" if sel else "transparent"};opacity:{"1" if sel else "0.6"};"><h4>{ic} {n}</h4><small>{de}</small></div>', unsafe_allow_html=True)
            if st.button(f"Choose {n}", use_container_width=True):
                st.session_state.temp_budget = n
                st.rerun()

    with st.form("step2"):
        pace = st.select_slider("Pace", options=["🐢 Relaxed", "⚖️ Balanced", "🚀 Packed"])
        interests = st.multiselect("Interests", ["🍜 Food", "🌿 Nature", "🎨 Art", "🧗 Adventure", "🌙 Nightlife"])
        c1, c2 = st.columns(2)
        if c1.form_submit_button("← Back"): st.session_state.step = 1; st.rerun()
        if c2.form_submit_button("Generate! 🚀"):
            st.session_state.trip_data.update({"budget": st.session_state.temp_budget, "pace": pace, "interests": interests})
            st.session_state.step = 3
            st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)

# ─────────────────────────────────────────
# STEP 3 — ITINERARY
# ─────────────────────────────────────────
elif st.session_state.step == 3:
    engine = get_engine(config.google_api_key)
    maps_client = get_maps_client(config.maps_api_key)
    
    if st.session_state.itinerary is None:
        render_loader()
        d = st.session_state.trip_data.get('dates', [])
        num = (d[1] - d[0]).days + 1 if len(d) == 2 else 3
        prefs = st.session_state.trip_data.copy(); prefs['days'] = num
        st.session_state.itinerary = engine.generate_itinerary(prefs)
        st.rerun()

    if st.session_state.itinerary and "error" not in st.session_state.itinerary:
        itin = st.session_state.itinerary
        st.markdown(f'<div class="floating-wishlist">💖 Wishlist <span>{len(st.session_state.wishlist)}</span></div>', unsafe_allow_html=True)
        
        m_col, s_col = st.columns([2, 1])
        with m_col:
            st.subheader(itin.get("trip_title"))
            for day in itin.get("days", []):
                dn = day['day_number']
                is_l = any(w['day_number'] == dn and w['trip'] == itin.get("trip_title") for w in st.session_state.wishlist)
                st.markdown(f'<div class="day-header"><h2>📅 Day {dn}</h2></div>', unsafe_allow_html=True)
                
                l1, l2 = st.columns([8, 1])
                with l2:
                    # The class 'love-btn-active' triggers the keyframe animation
                    btn_class = "love-btn-active" if is_l else "love-btn-inactive"
                    st.markdown(f'<div class="{btn_class}" style="margin-top:-65px;">', unsafe_allow_html=True)
                    if st.button("❤️", key=f"l_{dn}"):
                        if is_l: st.session_state.wishlist = [w for w in st.session_state.wishlist if not (w['day_number'] == dn and w['trip'] == itin.get('trip_title'))]
                        else: st.session_state.wishlist.append({'trip': itin.get('trip_title'), 'day_number': dn, 'slots': day['slots']})
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

                for s in day.get("slots", []):
                    det = maps_client.get_place_details(s['location_query'], config.maps_api_key)
                    st.markdown(f'<div class="time-slot-card accent-{s["time"].lower()} fade-in"><img src="{det.get("photo_url") or "https://via.placeholder.com/400"}" class="slot-image" alt="{s["activity"]}"><div class="slot-details"><h3>{s["time"]}: {s["activity"]}</h3><p>{s["description"]}</p><small>⭐ {det["rating"]} · {s["estimated_cost"]}</small></div></div>', unsafe_allow_html=True)

        with s_col:
            st.markdown("### 🗺️ Map View")
            render_itinerary_map(itin.get("days", []))
            if st.button("🔄 Reset"): st.session_state.step = 0; st.session_state.itinerary = None; st.rerun()
    st.button("← Start Over", on_click=lambda: st.session_state.update({"step": 0, "itinerary": None}))

# ─────────────────────────────────────────
# STEP 4 — WISHLIST
# ─────────────────────────────────────────
elif st.session_state.step == 4:
    st.markdown('<div class="fade-in"><h2>💖 Saved Adventures</h2>', unsafe_allow_html=True)
    if not st.session_state.wishlist:
        st.markdown('<div class="glass-card" style="text-align:center;padding:50px;"><h1>🏝️</h1><h3>Empty!</h3><p>Heart some days to save them.</p></div>', unsafe_allow_html=True)
        if st.button("Go Back"): st.session_state.step = 0; st.rerun()
    else:
        for i, item in enumerate(st.session_state.wishlist):
            st.markdown(f'<div class="glass-card" style="margin-bottom:15px;"><h3>{item["trip"]} - Day {item["day_number"]}</h3><ul>' + "".join([f'<li>{s["time"]}: {s["activity"]}</li>' for s in item["slots"]]) + '</ul></div>', unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Remove ✕", key=f"r_{i}"): st.session_state.wishlist.pop(i); st.rerun()
            if c2.button("Download 📥", key=f"d_{i}"): st.download_button("Save CSV", data="Time,Activity\n" + "\n".join([f'{s["time"]},{s["activity"]}' for s in item["slots"]]), file_name="day.csv")
        if st.button("← Back"): st.session_state.step = 0; st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<div class='voyage-footer'>VoyageAI 2026</div>", unsafe_allow_html=True)
config.validate()
