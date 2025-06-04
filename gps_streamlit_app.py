import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd

# Page setup
st.set_page_config(page_title="GPS Location App", layout="wide")
st.title("📍 Real-Time GPS Location Tracker")

# Sidebar
with st.sidebar:
    st.header("🧭 How It Works")
    st.markdown("""
    - This app retrieves your **GPS location** from your browser.
    - If location access is denied, you can manually enter coordinates.
    - The location is shown on a map and can be sent to a server.
    """)

# Try to get location using browser geolocation
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location"
)

# Case 1: Browser location access granted
if location and isinstance(location, dict) and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]

    st.success("✅ Location retrieved successfully!")
    st.metric("Latitude", f"{lat:.6f}")
    st.metric("Longitude", f"{lon:.6f}")

    st.subheader("🗺️ Your Location on Map")
    df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
    st.map(df)

    if st.button("📤 Send Coordinates to Server"):
        st.success(f"Coordinates sent: ({lat:.6f}, {lon:.6f})")

# Case 2: Fallback to manual input if location not available
else:
    st.warning("⚠️ Browser location not available or denied.")
    st.info("📌 Please allow location access or enter coordinates manually.")

    lat = st.number_input("Enter Latitude manually", format="%.6f", value=0.0)
    lon = st.number_input("Enter Longitude manually", format="%.6f", value=0.0)

    if st.button("📍 Show Location on Map"):
        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        st.map(df)
        st.success(f"Manual location set: ({lat:.6f}, {lon:.6f})")

        if st.button("📤 Send Manual Coordinates to Server"):
            st.success(f"Manual coordinates sent: ({lat:.6f}, {lon:.6f})")
