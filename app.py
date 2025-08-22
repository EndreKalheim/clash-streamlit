import streamlit as st
from pages import search, player_details
from parameters import check_api_connection

st.set_page_config(
    page_title="Clash of Clans Player Finder",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

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