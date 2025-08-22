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
    # Initialize session state for storing seen clan tags and found players
    if "seen_clan_tags" not in st.session_state:
        st.session_state.seen_clan_tags = set()
    
    if "found_players" not in st.session_state:
        st.session_state.found_players = []
    
    if "search_filters" not in st.session_state:
        st.session_state.search_filters = {}
        
    if "clans_searched" not in st.session_state:
        st.session_state.clans_searched = 0
    
    st.title("Clash of Clans Player Finder")
    st.subheader("Find active players based on customizable criteria")
    
    # Using tabs for better organization
    filter_tab, about_tab = st.tabs(["Search Filters", "About"])
    
    with filter_tab:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Clan Search Parameters")
            min_members = st.number_input("Minimum Clan Members", min_value=1, max_value=50, value=parameters.MIN_MEMBERS)
            max_members = st.number_input("Maximum Clan Members", min_value=10, max_value=200, value=parameters.MAX_MEMBERS)
            language_filter = st.text_input("Language Filter (e.g., 'en' for English)", value=parameters.LANGUAGE_FILTER)
            league_filter = st.text_input("League Filter (e.g., 'Crystal')", value=parameters.LEAGUE_FILTER)
            max_clans = st.slider("Maximum Clans to Search Per Run", 10, 500, 100, 10, 
                               help="Limit the number of clans to search for faster results")
        
        with col2:
            st.subheader("Player Filter Parameters")
            min_townhall = st.number_input("Minimum Town Hall Level", min_value=1, max_value=16, value=parameters.MIN_TOWNHALL)
            min_attack_wins = st.number_input("Minimum Attack Wins", min_value=0, max_value=1000, value=parameters.MIN_ATTACK_WINS)
            min_war_stars = st.number_input("Minimum War Stars", min_value=0, max_value=10000, value=parameters.MIN_WAR_STARS)
            min_trophies = st.number_input("Minimum Trophies", min_value=0, max_value=10000, value=parameters.MIN_TROPHIES)
            
            # Convert the excluded roles list to a comma-separated string for input
            default_excluded = ", ".join(parameters.EXCLUDE_ROLES)
            exclude_roles_input = st.text_input("Exclude Roles (comma-separated)", value=default_excluded)
            exclude_roles = [role.strip() for role in exclude_roles_input.split(",") if role.strip()]
    
    with about_tab:
        st.markdown("""
        ### How It Works
        
        This tool searches for active Clash of Clans players by:
        
        1. Finding clans that match your filter criteria
        2. Examining each clan's members for active players
        3. Filtering players based on your requirements
        
        ### Tips for Finding Players
        
        - Set Town Hall to 16 for the most competitive players
        - Higher war stars (500+) indicate experienced players
        - Look for players with 40+ attack wins per season
        - Crystal league clans often have more active players
        
        ### Continuing Searches
        
        After completing a search, you can click "Continue Search" to find more players.
        The app will remember which clans it has already checked and will only search new ones.
        """)
    
    # Create button row with conditional continue button
    col1, col2 = st.columns(2)
    
    with col1:
        if len(st.session_state.found_players) > 0:
            # Show stats about previous searches
            st.info(f"Previously found: {len(st.session_state.found_players)} players from {st.session_state.clans_searched} clans")
            new_search_button = st.button("Start New Search", type="primary", use_container_width=True)
        else:
            new_search_button = st.button("Search for Players", type="primary", use_container_width=True)
    
    with col2:
        # Only show continue button if we've already done a search
        if len(st.session_state.found_players) > 0:
            continue_search = st.button("Continue Search", type="secondary", use_container_width=True)
        else:
            continue_search = False
    
    # Start a new search (reset state)
    if new_search_button:
        # Reset session state
        st.session_state.seen_clan_tags = set()
        st.session_state.found_players = []
        st.session_state.clans_searched = 0
        continue_search = True  # Trigger the search flow
        
        # Store current search filters
        st.session_state.search_filters = {
            "min_members": min_members,
            "max_members": max_members,
            "language_filter": language_filter,
            "league_filter": league_filter,
            "max_clans": max_clans,
            "min_townhall": min_townhall,
            "min_attack_wins": min_attack_wins,
            "min_war_stars": min_war_stars,
            "min_trophies": min_trophies,
            "exclude_roles": exclude_roles
        }
    
    # If continuing search, use the stored filters
    if continue_search:
        # Set up progress tracking
        progress_bar = st.progress(0)
        status_container = st.container()
        results_container = st.container()
        
        # Use stored filters if continuing a search
        if len(st.session_state.found_players) > 0 and not new_search_button:
            filters = st.session_state.search_filters
            min_members = filters["min_members"]
            max_members = filters["max_members"]
            language_filter = filters["language_filter"]
            league_filter = filters["league_filter"]
            max_clans = filters["max_clans"]
            min_townhall = filters["min_townhall"]
            min_attack_wins = filters["min_attack_wins"]
            min_war_stars = filters["min_war_stars"]
            min_trophies = filters["min_trophies"]
            exclude_roles = filters["exclude_roles"]
        
        # Track local results for this search run
        found_clans = []
        newly_found_players = []
        
        # Status indicators
        clan_count = status_container.empty()
        player_count = status_container.empty()
        current_action = status_container.empty()
        
        current_action.info("Starting search...")
        clan_count.metric("Clans Found", len(found_clans))
        player_count.metric("Players Found", len(st.session_state.found_players))
        
        # Define callback for progress updates
        def progress_callback(progress_type, data):
            if progress_type == "clan_found":
                found_clans.append(data)
                clan_count.metric("Clans Found", f"{len(found_clans)} (this run) / {st.session_state.clans_searched + len(found_clans)} (total)")
                progress_bar.progress(min(len(found_clans) / max_clans, 0.95) if max_clans else 0.5)
                current_action.info(f"Searching clan: {data.get('name', 'Unknown')}") 
            elif progress_type == "player_found":
                newly_found_players.append(data)
                st.session_state.found_players.append(data)
                player_count.metric("Players Found", f"{len(newly_found_players)} (this run) / {len(st.session_state.found_players)} (total)")
                current_action.success(f"Found player: {data.get('name', 'Unknown')}")
        
        # Call the optimized search function (uses the API key from parameters)
        current_action.info("Searching for clans and players...")
        
        # Pass the existing seen_clan_tags set to avoid duplicates
        new_players = search_players_optimized(
            min_townhall=min_townhall,
            min_attack_wins=min_attack_wins,
            min_war_stars=min_war_stars,
            min_trophies=min_trophies,
            language_filter=language_filter,
            league_filter=league_filter,
            exclude_roles=exclude_roles,
            min_members=min_members,
            max_members=max_members,
            max_clans=max_clans,
            seen_clan_tags=st.session_state.seen_clan_tags,  # Pass existing seen tags
            progress_callback=progress_callback
        )
        
        # Update session state
        st.session_state.clans_searched += len(found_clans)
        
        progress_bar.progress(100)
        current_action.success(f"Search complete! Found {len(newly_found_players)} new players in this run.")
        
        # Display results
        with results_container:
            if newly_found_players:
                st.subheader("Newly Found Players")
                
                # Convert to Polars DataFrame for better display
                player_data = []
                for player in newly_found_players:
                    player_data.append({
                        "Name": player.get("name", "Unknown"),
                        "Tag": player.get("tag", "Unknown"),
                        "Town Hall": player.get("townHallLevel", 0),
                        "Trophies": player.get("trophies", 0),
                        "War Stars": player.get("warStars", 0),
                        "Attack Wins": player.get("attackWins", 0),
                        "Clan": player.get("clan", {}).get("name", "No Clan")
                    })
                
                new_df = pl.DataFrame(player_data)
                st.dataframe(new_df, use_container_width=True)
                
            if st.session_state.found_players:
                st.subheader("All Found Players")
                
                # Convert to Polars DataFrame for all players
                all_player_data = []
                for player in st.session_state.found_players:
                    all_player_data.append({
                        "Name": player.get("name", "Unknown"),
                        "Tag": player.get("tag", "Unknown"),
                        "Town Hall": player.get("townHallLevel", 0),
                        "Trophies": player.get("trophies", 0),
                        "War Stars": player.get("warStars", 0),
                        "Attack Wins": player.get("attackWins", 0),
                        "Clan": player.get("clan", {}).get("name", "No Clan")
                    })
                
                all_df = pl.DataFrame(all_player_data)
                
                # Export options
                export_col1, export_col2, export_col3 = st.columns(3)
                
                with export_col1:
                    # Export as CSV
                    csv_data = all_df.write_csv().encode('utf-8')
                    st.download_button(
                        label="Export as CSV",
                        data=csv_data,
                        file_name="clash_players.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                with export_col2:
                    # Export as JSON
                    json_data = json.dumps(st.session_state.found_players, indent=2).encode('utf-8')
                    st.download_button(
                        label="Export as JSON",
                        data=json_data,
                        file_name="clash_players.json",
                        mime="application/json",
                        use_container_width=True
                    )
                
                with export_col3:
                    # Export just the player tags without #, one per line
                    tags_only = [tag.replace('#', '') for tag in all_df.get_column("Tag").to_list()]
                    tags_text = '\n'.join(tags_only)
                    
                    st.download_button(
                        label="Export Player Tags Only",
                        data=tags_text.encode('utf-8'),
                        file_name="player_tags.txt",
                        mime="text/plain",
                        use_container_width=True
                    )
                
                # Show dataframe with all players
                st.dataframe(all_df, use_container_width=True)
            else:
                st.error("No active players found matching your criteria. Try adjusting your filters.")

if __name__ == "__main__":
    run()