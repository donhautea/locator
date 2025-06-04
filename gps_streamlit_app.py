# gps_streamlit_app.py

import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd

# Page config
st.set_page_config(page_title="User Location App", layout="wide")
st.title("📍 Real-Time User Location Tracker")

# Sidebar info
with st.sidebar:
    st.header("📌 App Info")
    st.markdown("""
    - This app retrieves your current GPS coordinates.
    - It uses your browser's location permission.
    - Location is visualized on the map.
    """)

# Get location using JS eval (via browser)
location = streamlit_js_eval(js_expressions="navigator.geolocation.getCurrentPosition", key="get_location", timeout=30)

if location and isinstance(location, dict) and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    
    st.success("📍 Location retrieved successfully!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Latitude", f"{lat:.6f}")
    with col2:
        st.metric("Longitude", f"{lon:.6f}")

    # Show location on map
    st.subheader("🗺️ Current Location on Map")
    location_df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
    st.map(location_df)

    # Button to simulate sending to server
    if st.button("🚀 Send Coordinates to Server"):
        # Simulate server send (you can replace this with actual backend call)
        st.success(f"Coordinates sent: ({lat:.6f}, {lon:.6f})")
else:
    st.warning("⚠️ Please allow location access in your browser.")
