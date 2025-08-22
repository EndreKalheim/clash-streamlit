# Default parameters for the Clash of Clans API
import streamlit as st

# API Configuration
try:
    # Try to get API key from Streamlit secrets for deployed environment
    API_KEY = st.secrets["API_KEY"]
except Exception:
    # Fall back to hardcoded key for local development
    API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjE4OTcxYTQ5LTk2ZDgtNGJlNy1hN2MwLTBkYTVhY2FmNDRlMiIsImlhdCI6MTc1NTg3MzA3OSwic3ViIjoiZGV2ZWxvcGVyL2NhNmM2NDQyLTZjYTUtZDk4ZS1mNjNiLWFkYjhmZTIwNTU3YSIsInNjb3BlcyI6WyJjbGFzaCJdLCJsaW1pdHMiOlt7InRpZXIiOiJkZXZlbG9wZXIvc2lsdmVyIiwidHlwZSI6InRocm90dGxpbmcifSx7ImNpZHJzIjpbIjE4OC4xMTMuOTAuMjQ2IiwiNDUuNzkuMjE4Ljc5Il0sInR5cGUiOiJjbGllbnQifV19.oPnLIGeT5uXe8_uGg5YHldNh41NL30vUOKkqKppiOyCD03JSkYUCh-5iwDTmAaiTgxRNmwWfcH8iusQshdG8mQ"

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