# gps_location_app.py

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd

# Page Configuration
st.set_page_config(page_title="User GPS Locator", layout="wide")

# Title and Sidebar
st.title("📍 Real-Time GPS Location Tracker")
with st.sidebar:
    st.header("🌐 Instructions")
    st.markdown("""
    - Make sure to **allow location access** when prompted by your browser.
    - This app will fetch your **current coordinates** and show your **location on a map**.
    - Works best on Chrome, Edge, or Safari with location enabled.
    """)

# Fetch current location using JS API
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location"
)

# Process and Display Location
if location and isinstance(location, dict) and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]

    st.success("✅ Location retrieved successfully!")

    # Show coordinates
    col1, col2 = st.columns(2)
    col1.metric("Latitude", f"{lat:.6f}")
    col2.metric("Longitude", f"{lon:.6f}")

    # Show on map
    st.subheader("🗺️ Your Location on Map")
    df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
    st.map(df)

    # Simulate sending to server
    if st.button("📤 Send Coordinates to Server"):
        st.success(f"Coordinates sent: ({lat:.6f}, {lon:.6f})")

else:
    st.warning("⚠️ Please allow location access in your browser settings.")
    st.info("📌 If you blocked it, reset permissions and reload this page.")
