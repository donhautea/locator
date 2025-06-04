import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import requests

# Set Streamlit page configuration
st.set_page_config(page_title="GPS Location App", layout="wide")
st.title("📍 Real-Time GPS Location Tracker")

# Sidebar
with st.sidebar:
    st.header("🧭 How It Works")
    st.markdown("""
    - Retrieves your **GPS location** via browser (precise).
    - Falls back to **IP-based location** if GPS is denied or blocked.
    - Allows **manual entry** if both fail.
    """)

# Fallback IP-based location
def get_location_from_ip():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return float(res['latitude']), float(res['longitude'])
    except Exception as e:
        return None, None

# Try to get location from browser
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location"
)

# --- CASE 1: Browser-based location (accurate) ---
if location and isinstance(location, dict) and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]

    st.success("✅ Accurate browser-based location retrieved.")
    st.metric("Latitude", f"{lat:.6f}")
    st.metric("Longitude", f"{lon:.6f}")
    st.subheader("🗺️ Your Location on Map")
    df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
    st.map(df)

    if st.button("📤 Send Coordinates to Server"):
        st.success(f"Coordinates sent: ({lat:.6f}, {lon:.6f})")

# --- CASE 2: Fallback to IP-based geolocation ---
else:
    st.warning("⚠️ Unable to retrieve precise location from browser. Trying fallback...")

    lat, lon = get_location_from_ip()
    if lat is not None and lon is not None:
        st.info("🌐 IP-based approximate location retrieved.")
        st.metric("Approx. Latitude", f"{lat:.6f}")
        st.metric("Approx. Longitude", f"{lon:.6f}")
        st.subheader("🗺️ Approximate Location on Map")
        df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
        st.map(df)

        if st.button("📤 Send Approx. Coordinates to Server"):
            st.success(f"Approx. coordinates sent: ({lat:.6f}, {lon:.6f})")
    else:
        st.error("❌ Fallback location failed. Please enter manually.")

        # --- CASE 3: Manual location entry ---
        lat = st.number_input("📌 Enter Latitude manually", format="%.6f", value=0.0)
        lon = st.number_input("📌 Enter Longitude manually", format="%.6f", value=0.0)

        if st.button("📍 Show Manual Location on Map"):
            df = pd.DataFrame([[lat, lon]], columns=["lat", "lon"])
            st.map(df)
            st.success(f"Manual location shown: ({lat:.6f}, {lon:.6f})")

            if st.button("📤 Send Manual Coordinates to Server"):
                st.success(f"Manual coordinates sent: ({lat:.6f}, {lon:.6f})")
