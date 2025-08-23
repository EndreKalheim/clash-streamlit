# filepath: clash-script/pages/search.py

import streamlit as st
import time
import polars as pl
import sys
import os
import json

# Add parent directory to path to import from parameters
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api import search_players_optimized
import parameters

def run():
    """Run the Search Players page."""
    st.title("Search for Active Players")

    with st.form("search_parameters"):
        st.subheader("Search Parameters")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Player criteria
            min_townhall = st.slider("Minimum Town Hall Level", min_value=1, max_value=16, value=16)
            min_attack_wins = st.slider("Minimum Attack Wins", min_value=0, max_value=5000, value=40)
            min_war_stars = st.slider("Minimum War Stars", min_value=0, max_value=5000, value=500)
            min_trophies = st.slider("Minimum Trophies", min_value=0, max_value=8000, value=4500)
            
        with col2:
            # Clan criteria
            language_filter = st.selectbox(
                "Clan Language", 
                options=[
                    ("English", "en"), 
                    ("French", "fr"), 
                    ("German", "de"), 
                    ("Italian", "it"), 
                    ("Spanish", "es"), 
                    ("Russian", "ru"), 
                    ("Any Language", None)
                ],
                format_func=lambda x: x[0],
                index=0
            )
            
            league_filter = st.selectbox(
                "Clan War League", 
                options=[
                    "Champion", 
                    "Master", 
                    "Crystal", 
                    "Gold", 
                    "Silver", 
                    "Bronze", 
                    None
                ],
                index=2
            )
            
            clan_size_min, clan_size_max = st.slider(
                "Clan Size (members)", 
                min_value=1, 
                max_value=50,
                value=(10, 50)
            )
            
            max_clans = st.slider(
                "Maximum Clans to Search", 
                min_value=10, 
                max_value=1000, 
                value=100
            )
            
            exclude_roles = st.multiselect(
                "Exclude Roles", 
                options=["leader", "coLeader", "admin", "member"],
                default=["leader"]
            )

        submitted = st.form_submit_button("Search")
    
    if submitted:
        # Create the progress bars and counters
        progress_placeholder = st.empty()
        with progress_placeholder.container():
            clans_progress = st.progress(0)
            clans_text = st.empty()
            current_clan = st.empty()
            player_progress = st.progress(0)
            player_text = st.empty()

        # Reset session state for results
        st.session_state.clans_searched = 0
        st.session_state.players_found = []
        
        # Extract language code from tuple if needed
        language_code = language_filter[1] if isinstance(language_filter, tuple) else language_filter

        # Define the progress callback
        def progress_callback(event_type, data):
            if event_type == "clan_found":
                st.session_state.clans_searched += 1
                clans_text.write(f"Clans searched: {st.session_state.clans_searched}")
                clans_progress.progress(min(st.session_state.clans_searched / max_clans, 1.0))
            elif event_type == "clan_processing":
                current_clan.write(f"Checking clan: {data['name']} ({data['tag']})")
            elif event_type == "player_found":
                st.session_state.players_found.append(data)
                player_text.write(f"Players found: {len(st.session_state.players_found)}")
                # Assuming we target around 100 players max for a reasonable search
                player_progress.progress(min(len(st.session_state.players_found) / 100, 1.0))
        
        # Run the search with all the parameters from the form
        with st.spinner("Searching for active players..."):
            players = search_players_optimized(
                min_townhall=min_townhall,
                min_attack_wins=min_attack_wins,
                min_war_stars=min_war_stars,
                min_trophies=min_trophies,
                language_filter=language_code,
                league_filter=league_filter,
                exclude_roles=exclude_roles,
                min_members=clan_size_min,
                max_members=clan_size_max,
                max_clans=max_clans,
                progress_callback=progress_callback
            )
            
        # Clear progress display
        progress_placeholder.empty()
        
        # Store results in session state
        st.session_state.search_results = players
        
        # Show results summary
        st.success(f"Search complete! Found {len(players)} active players.")
        
        # Display results
        display_player_results(players)
    
    # Show previous results if available
    elif "search_results" in st.session_state and st.session_state.search_results:
        st.info(f"Showing previous search results ({len(st.session_state.search_results)} players).")
        display_player_results(st.session_state.search_results)

def display_player_results(players):
    """Display the player results in a structured table."""
    if not players:
        st.warning("No players found. Try adjusting your search parameters.")
        return
    
    # Convert player data to DataFrame for display
    player_data = []
    for player in players:
        player_data.append({
            "Name": player.get("name", "Unknown"),
            "Tag": player.get("tag", "Unknown"),
            "Town Hall": player.get("townHallLevel", 0),
            "Trophies": player.get("trophies", 0),
            "War Stars": player.get("warStars", 0),
            "Attack Wins": player.get("attackWins", 0),
            "Clan": player.get("clan", {}).get("name", "No Clan")
        })
    
    df = pl.DataFrame(player_data)
    
    # Display the DataFrame in Streamlit
    st.dataframe(df, use_container_width=True)
    
    # Export options
    export_col1, export_col2, export_col3 = st.columns(3)
    
    with export_col1:
        # Export as CSV
        csv_data = df.write_csv().encode('utf-8')
        st.download_button(
            label="Export as CSV",
            data=csv_data,
            file_name="clash_players.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with export_col2:
        # Export as JSON
        json_data = json.dumps(players, indent=2).encode('utf-8')
        st.download_button(
            label="Export as JSON",
            data=json_data,
            file_name="clash_players.json",
            mime="application/json",
            use_container_width=True
        )
    
    with export_col3:
        # Export just the player tags without #, one per line
        tags_only = [tag.replace('#', '') for tag in df.get_column("Tag").to_list()]
        tags_text = '\n'.join(tags_only)
        
        st.download_button(
            label="Export Player Tags Only",
            data=tags_text.encode('utf-8'),
            file_name="player_tags.txt",
            mime="text/plain",
            use_container_width=True
        )