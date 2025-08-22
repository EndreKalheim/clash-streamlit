import streamlit as st
from pages import search, player_details

st.set_page_config(
    page_title="Clash of Clans Player Finder",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

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