import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import pandas as pd
import requests
import gspread
from datetime import datetime
from oauth2client.service_account import ServiceAccountCredentials

# Set up page layout
st.set_page_config(page_title="Mobile GPS Logger", layout="wide")
st.title("📍 Mobile Location Logger")

# Sidebar
with st.sidebar:
    st.header("🧭 How It Works")
    st.markdown("""
    - Retrieves your location via **GPS (browser)**.
    - Falls back to **IP-based location** if GPS fails.
    - You can **manually enter** coordinates too.
    - All locations are saved to a **Google Sheet**.
    """)

# --- Google Sheets Authentication ---
def authorize_gsheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", scope)
    client = gspread.authorize(creds)
    return client

# --- Append coordinates to Google Sheet ---
def log_to_google(lat, lon, method):
    client = authorize_gsheet()
    sheet = client.open("LocationLogger").sheet1
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sheet.append_row([now, lat, lon, method])
    return True

# --- IP-based fallback ---
def get_location_from_ip():
    try:
        res = requests.get("https://ipapi.co/json/").json()
        return float(res['latitude']), float(res['longitude'])
    except:
        return None, None

# --- Try to get location from browser GPS ---
location = streamlit_js_eval(
    js_expressions="navigator.geolocation.getCurrentPosition",
    key="get_location",
    label="Get user location"
)

# --- CASE 1: Browser GPS location available ---
if location and isinstance(location, dict) and "coords" in location:
    lat = location["coords"]["latitude"]
    lon = location["coords"]["longitude"]
    method = "Browser GPS"

    st.success("✅ GPS Location retrieved successfully!")
    st.metric("Latitude", f"{lat:.6f}")
    st.metric("Longitude", f"{lon:.6f}")
    st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

    if st.button("📤 Send Coordinates to Google Sheet"):
        if log_to_google(lat, lon, method):
            st.success(f"Coordinates sent to Google Sheet via {method}")

# --- CASE 2: Fallback to IP-based location ---
else:
    st.warning("⚠️ GPS not available. Trying IP-based location...")
    lat, lon = get_location_from_ip()
    method = "IP-based"

    if lat is not None and lon is not None:
        st.info("🌐 IP-based approximate location retrieved.")
        st.metric("Latitude", f"{lat:.6f}")
        st.metric("Longitude", f"{lon:.6f}")
        st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))

        if st.button("📤 Send IP-based Coordinates to Google Sheet"):
            if log_to_google(lat, lon, method):
                st.success(f"Coordinates sent to Google Sheet via {method}")
    else:
        # --- CASE 3: Manual entry fallback ---
        st.error("❌ IP-based fallback failed. Please enter coordinates manually.")
        lat = st.number_input("Enter Latitude manually", format="%.6f", value=0.0)
        lon = st.number_input("Enter Longitude manually", format="%.6f", value=0.0)
        method = "Manual"

        if st.button("📍 Show Manual Location on Map"):
            st.map(pd.DataFrame([[lat, lon]], columns=["lat", "lon"]))
            st.success(f"Manual location: ({lat:.6f}, {lon:.6f})")

        if st.button("📤 Send Manual Coordinates to Google Sheet"):
            if log_to_google(lat, lon, method):
                st.success(f"Manual coordinates sent to Google Sheet")
