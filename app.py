import streamlit as st
from pages import search, player_details
from parameters import check_api_connection, API_KEY, BASE_URL
import requests
import json
import traceback

st.set_page_config(
    page_title="Clash of Clans Player Finder",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Global variable to store API call logs
if "api_calls" not in st.session_state:
    st.session_state.api_calls = []

# Override requests.get to log all API calls
original_get = requests.get
def logging_get(*args, **kwargs):
    try:
        url = args[0] if args else kwargs.get('url', 'Unknown URL')
        st.session_state.api_calls.append({"url": url, "status": "Attempting..."})
        index = len(st.session_state.api_calls) - 1
        
        response = original_get(*args, **kwargs)
        
        call_info = {
            "url": url,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response": response.text[:100] + "..." if len(response.text) > 100 else response.text
        }
        st.session_state.api_calls[index] = call_info
        return response
    except Exception as e:
        error_info = {
            "url": url,
            "status_code": "Error",
            "success": False,
            "response": str(e),
            "traceback": traceback.format_exc()
        }
        st.session_state.api_calls[index] = error_info
        raise e

# Replace requests.get with our logging version
requests.get = logging_get

# Check API connection silently (no UI feedback unless there's an error)
api_working, api_message = check_api_connection()
if not api_working:
    st.error(f"API Connection Error: {api_message}")
    st.info("If deployed on Streamlit Cloud, make sure the RoyaleAPI proxy IP (45.79.218.79) is whitelisted in your Clash API key settings.")
    st.stop()

def main():
    # Sidebar for navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Search Players", "Player Details"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("### About")
    st.sidebar.info(
        """
        This app helps you find active Clash of Clans players 
        based on customizable criteria.
        
        Use the Search page to find players, then view detailed 
        information on the Player Details page.
        """
    )

    if page == "Search Players":
        search.run()
    elif page == "Player Details":
        player_details.run()

if __name__ == "__main__":
    main()