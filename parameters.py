# Default parameters for the Clash of Clans API
import streamlit as st
import requests
import json

# API Configuration
try:
    # Try to get API key from Streamlit secrets for deployed environment
    API_KEY = st.secrets["API_KEY"]
except Exception:
    # Fall back to hardcoded key for local development
    API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjAzMDZlZWIyLWQxZjgtNDJhZC05ZGVmLTRjZmExNTRiMGRjNSIsImlhdCI6MTc1NTkwMzIyMiwic3ViIjoiZGV2ZWxvcGVyL2NhNmM2NDQyLTZjYTUtZDk4ZS1mNjNiLWFkYjhmZTIwNTU3YSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjE4OC4xMTMuOTAuMjQ2IiwiNDUuNzkuMjE4Ljc5IiwiMzUuMjAzLjE1MS4xMDEiXSwidHlwZSI6ImNsaWVudCJ9XX0.zHUSJWaK4M2KYfrseuuUOg_SkZ7RJG1Y6rKeKMpQsb9BW68_CPC1ydUSPwuFnMra5Z2EHsPBV1PnNDgqrvQr1Q"

# Base URL - Set to use RoyaleAPI proxy instead of direct API calls
BASE_URL = "https://cocproxy.royaleapi.dev/v1"

THREADS = 20

# Clan Search Parameters
MIN_MEMBERS = 10
MAX_MEMBERS = 200

# Player Filter Parameters
MIN_TOWNHALL = 16
MIN_ATTACK_WINS = 40
MIN_WAR_STARS = 500
MIN_TROPHIES = 4500

# Filter options
LANGUAGE_FILTER = "en"  # Set to empty string to disable language filtering
LEAGUE_FILTER = "Crystal"  # Set to empty string to disable league filtering
EXCLUDE_ROLES = ["leader"]  # Roles to exclude when searching for players

# Function to check API connectivity
def check_api_connection():
    """Check if the API connection is working properly"""
    headers = {"Authorization": f"Bearer {API_KEY}"}
    test_url = f"{BASE_URL}/locations"
    
    try:
        response = requests.get(test_url, headers=headers)
        if response.status_code == 200:
            return True, "API connection successful"
        else:
            return False, f"API Error: {response.status_code} - {response.text}"
    except Exception as e:
        return False, f"Connection Error: {str(e)}"
