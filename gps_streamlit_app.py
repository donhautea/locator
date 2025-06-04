# app.py

import streamlit as st
import pandas as pd
from streamlit_geolocation import streamlit_geolocation

# Page configuration
st.set_page_config(page_title="Geolocation Map", layout="wide")

st.title("📍 Find My Location")
st.write(
    """
    Click the circular button below to share your current location. 
    Once allowed, your latitude/longitude will be plotted on a map.
    """
)

# The streamlit-geolocation component renders a circular "Get Location" button.
# At first it returns "No Location Info" until pressed.
location_data = streamlit_geolocation()

# If the user has granted permission and we successfully received coords,
# location_data will be a dict containing at least 'latitude' and 'longitude'.
if isinstance(location_data, dict) and "latitude" in location_data:
    lat = location_data["latitude"]
    lon = location_data["longitude"]

    st.success(f"Location found: {lat:.6f}, {lon:.6f}")

    # Build a DataFrame suitable for st.map()
    df = pd.DataFrame([{"lat": lat, "lon": lon}])
    st.map(df)

else:
    st.info("Waiting for you to click the button and grant location permission.")
