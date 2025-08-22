import streamlit as st
from pages import search, player_details
from parameters import check_api_connection, API_KEY, BASE_URL
import requests

st.set_page_config(
    page_title="Clash of Clans Player Finder",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Debug mode toggle in sidebar
with st.sidebar:
    debug_mode = st.checkbox("Show API Diagnostics", value=True)

if debug_mode:
    st.subheader("API Connection Diagnostics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("API Configuration:")
        st.code(f"Base URL: {BASE_URL}")
        # Only show first/last 5 chars of API key for security
        masked_key = f"{API_KEY[:5]}...{API_KEY[-5:]}" if len(API_KEY) > 10 else "Not set"
        st.code(f"API Key: {masked_key}")
    
    with col2:
        # Test direct API and proxy API
        st.write("Connection Tests:")
        
        # Test RoyaleAPI proxy
        if st.button("Test RoyaleAPI Proxy"):
            api_working, api_message = check_api_connection()
            if api_working:
                st.success(f"✅ RoyaleAPI Proxy: {api_message}")
            else:
                st.error(f"❌ RoyaleAPI Proxy: {api_message}")
        
        # Test direct API too
        if st.button("Test Direct API"):
            headers = {"Authorization": f"Bearer {API_KEY}"}
            try:
                response = requests.get("https://api.clashofclans.com/v1/locations", headers=headers)
                if response.status_code == 200:
                    st.success(f"✅ Direct API: Connection successful")
                else:
                    st.error(f"❌ Direct API: Error {response.status_code} - {response.text}")
            except Exception as e:
                st.error(f"❌ Direct API: {str(e)}")
    
    st.markdown("---")

# Check API connection and display status
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