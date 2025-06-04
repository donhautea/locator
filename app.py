# app.py

import streamlit as st
import pandas as pd
import io
import os
from datetime import datetime

from streamlit_geolocation import streamlit_geolocation

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaIoBaseUpload

# --- GOOGLE DRIVE SETUP --------------------------------------------------------------------------------

SCOPES = ["https://www.googleapis.com/auth/drive.file"]
CSV_FILENAME = "coordinates.csv"


def get_drive_service():
    """
    Returns an authorized Drive v3 service instance.
    Expects 'credentials.json' in working directory. 
    On first run, opens browser for OAuth consent and saves token.json.
    """
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If no valid creds, go through the OAuth flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for next run
        with open("token.json", "w") as token_file:
            token_file.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


def append_to_drive_csv(service, row_dict):
    """
    1. Searches for CSV_FILENAME in Drive (mimeType='text/csv').
    2. If found: downloads it, appends row_dict to it, and re-uploads (update).
       If not found: creates a new DataFrame with headers, appends, and creates the file.
    """
    # 1) Search for existing file
    query = f"name='{CSV_FILENAME}' and mimeType='text/csv'"
    response = (
        service.files()
        .list(q=query, spaces="drive", fields="files(id, name)")
        .execute()
    )
    files = response.get("files", [])

    if files:
        # existing file → download & append
        file_id = files[0]["id"]

        # Download the CSV's contents into a BytesIO buffer
        request = service.files().get_media(fileId=file_id)
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
        fh.seek(0)

        # Load into DataFrame
        try:
            df = pd.read_csv(fh)
        except pd.errors.EmptyDataError:
            df = pd.DataFrame(columns=["timestamp", "latitude", "longitude"])
    else:
        # no existing file → create a new DataFrame with headers
        df = pd.DataFrame(columns=["timestamp", "latitude", "longitude"])
        # Create an empty file in Drive so we can update it later
        file_metadata = {"name": CSV_FILENAME, "mimeType": "text/csv"}
        created = service.files().create(body=file_metadata).execute()
        file_id = created.get("id")

    # 2) Append the new row
    df = df.append(row_dict, ignore_index=True)

    # 3) Convert DataFrame back to CSV and upload (overwrite)
    buffer = io.BytesIO()
    df.to_csv(buffer, index=False)
    buffer.seek(0)
    media = MediaIoBaseUpload(buffer, mimetype="text/csv", resumable=True)
    service.files().update(fileId=file_id, media_body=media).execute()


# --- STREAMLIT APP ---------------------------------------------------------------------------------------

st.set_page_config(page_title="Geolocation → Drive", layout="wide")
st.title("📍 Geolocation → Google Drive CSV")
st.write(
    """
    1. Click the circular button to share your location.  
    2. Once allowed, your latitude/longitude will plot on a map.  
    3. The coordinates (with a timestamp) are appended to **`coordinates.csv`** in your Google Drive.
    """
)

# Render "Get Location" button (streamlit-geolocation)
location_data = streamlit_geolocation()

if (
    isinstance(location_data, dict)
    and location_data.get("latitude") is not None
    and location_data.get("longitude") is not None
):
    # Try to parse floats
    try:
        lat = float(location_data["latitude"])
        lon = float(location_data["longitude"])
    except (TypeError, ValueError):
        st.error("Received location data in an unexpected format.")
    else:
        st.success(f"Location found: {lat:.6f}, {lon:.6f}")
        df = pd.DataFrame([{"lat": lat, "lon": lon}])
        st.map(df)

        # Prepare the row to append
        now_iso = datetime.now().isoformat(timespec="seconds")
        new_row = {"timestamp": now_iso, "latitude": lat, "longitude": lon}

        try:
            drive_service = get_drive_service()
            append_to_drive_csv(drive_service, new_row)
            st.info(f"✓ Appended to Drive: **{CSV_FILENAME}**")
        except Exception as e:
            st.error(f"⚠️ Could not write to Drive: {e}")

else:
    st.info("Waiting for you to click the button and grant location permission.")
