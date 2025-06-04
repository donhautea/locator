import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd

# Configure page layout
st.set_page_config(page_title="GPS Location App", layout="wide")
st.title("📍 Real-Time GPS Location Tracker")

# Sidebar Instructions
with st.sidebar:
    st.header("🧭 How It Works")
    st.markdown("""
    - This app requests your **GPS location** through your browser.
    - If permission is denied or not available, you can **manually enter coordinates**.
    - Your current location is shown on an interactive map.
    """)

# Try to get location using browser geolocation
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location"
)

# Case 1: Browser location retrieved successfully
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

# Case 2: Browser denied or failed to provide location
else:
    st.error("❌ Unable to retrieve location from browser.")
    st.markdown("""
    **Possible reasons:**
    - You denied the browser permission.
    - The browser didn’t prompt for location access.
    - Location Services are disabled on your device.
    
    🔄 Try refreshing the page and allow location access when prompted.
    
    Alternatively, you may enter your location manually:
    """)

    lat = st.number_input("📌 Enter Latitude manually", format="%.6f", value=0.0)
    lon = st.number_input("📌 Enter Longitude manually", format="%.6f", value=0.0)

    if st.button("📍 Show Manual Location on Map"):
        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        st.map(df)
        st.success(f"Manual location shown: ({lat:.6f}, {lon:.6f})")

        if st.button("📤 Send Manual Coordinates to Server"):
            st.success(f"Manual coordinates sent: ({lat:.6f}, {lon:.6f})")
