import streamlit as st
import sys
import os
import json
import polars as pl
from io import BytesIO

# Add parent directory to path to import from parameters
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.api import get_player_info
import parameters
from parameters import BASE_URL

def run():
    st.title("Player Details")
    
    # Check if we have players in the session state
    if "found_players" in st.session_state and st.session_state.found_players:
        saved_players = st.session_state.found_players
        have_saved_data = True
    else:
        have_saved_data = False
        st.info("No player data available. Use the Search tab to find players first.")
        return
    
    if have_saved_data:
        st.subheader("Browse found players")
        
        # Convert to Polars DataFrame for filtering
        player_data = []
        for player in saved_players:
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
        
        # Add filters in a sidebar for better UI
        st.sidebar.header("Filter Players")
        
        # Add filters
        min_th = st.sidebar.slider("Min Town Hall", min_value=1, max_value=16, value=parameters.MIN_TOWNHALL)
        min_trophies = st.sidebar.slider("Min Trophies", min_value=0, max_value=8000, value=parameters.MIN_TROPHIES)
        min_war_stars = st.sidebar.slider("Min War Stars", min_value=0, max_value=5000, value=parameters.MIN_WAR_STARS)
        min_attack_wins = st.sidebar.slider("Min Attack Wins", min_value=0, max_value=500, value=parameters.MIN_ATTACK_WINS)
        
        # Filter Polars DataFrame
        filtered_df = df.filter(
            (pl.col("Town Hall") >= min_th) &
            (pl.col("Trophies") >= min_trophies) &
            (pl.col("War Stars") >= min_war_stars) &
            (pl.col("Attack Wins") >= min_attack_wins)
        )
        
        # Create export section
        export_col1, export_col2, export_col3 = st.columns(3)
        
        with export_col1:
            # Export as CSV
            if st.button("Export as CSV", use_container_width=True):
                csv_data = filtered_df.write_csv().encode('utf-8')
                st.download_button(
                    label="Download CSV",
                    data=csv_data,
                    file_name="clash_players.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        with export_col2:
            # Export as JSON
            if st.button("Export as JSON", use_container_width=True):
                # Filter the full player data to match the filtered DataFrame
                filtered_tags = set(filtered_df.get_column("Tag").to_list())
                filtered_players = [p for p in saved_players if p.get("tag") in filtered_tags]
                
                json_data = json.dumps(filtered_players, indent=2).encode('utf-8')
                st.download_button(
                    label="Download JSON",
                    data=json_data,
                    file_name="clash_players.json",
                    mime="application/json",
                    use_container_width=True
                )
        
        with export_col3:
            # Export just the player tags without #, one per line
            if st.button("Export Player Tags Only", use_container_width=True):
                # Extract tags without the # character
                tags_only = [tag.replace('#', '') for tag in filtered_df.get_column("Tag").to_list()]
                tags_text = '\n'.join(tags_only)
                
                st.download_button(
                    label="Download Tags",
                    data=tags_text.encode('utf-8'),
                    file_name="player_tags.txt",
                    mime="text/plain",
                    use_container_width=True
                )
        
        # Display filtered data
        st.write(f"Showing {len(filtered_df)} players (filtered from {len(saved_players)} total)")
        st.dataframe(filtered_df, use_container_width=True)
        
        # Allow selecting players to view details
        if not filtered_df.is_empty():
            # Convert to list for selectbox
            tags_list = filtered_df.get_column("Tag").to_list()
            names_list = filtered_df.get_column("Name").to_list()
            
            # Create display options
            display_options = [f"{name} ({tag})" for name, tag in zip(names_list, tags_list)]
            selected_option = st.selectbox("Select a player to view details", options=display_options)
            
            # Extract tag from selection
            selected_tag = selected_option.split("(")[1].split(")")[0]
            
            if st.button("View Selected Player Details", type="primary"):
                player = next((p for p in saved_players if p["tag"] == selected_tag), None)
                if player:
                    display_player_details(player)
        else:
            st.info("No players match your filter criteria.")

def display_player_details(player):
    """Display detailed information about a player."""
    st.header(f"{player['name']} ({player['tag']})")
    
    # Layout with columns
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Player Stats")
        st.write(f"🏆 Trophies: {player.get('trophies', 0)}")
        st.write(f"🌟 War Stars: {player.get('warStars', 0)}")
        st.write(f"🏠 Town Hall: {player.get('townHallLevel', 0)}")
        st.write(f"⚔️ Attack Wins: {player.get('attackWins', 0)}")
        st.write(f"🛡️ Defense Wins: {player.get('defenseWins', 0)}")
        
    with col2:
        st.subheader("Clan Information")
        clan = player.get("clan", {})
        if clan:
            st.write(f"🏰 Clan: {clan.get('name', 'None')}")
            st.write(f"📋 Tag: {clan.get('tag', 'None')}")
            st.write(f"📈 Level: {clan.get('clanLevel', 0)}")
            st.write(f"🏅 Role: {player.get('role', 'Unknown')}")
        else:
            st.write("No clan")
    
    # Donations section
    st.subheader("Donations")
    col3, col4 = st.columns(2)
    with col3:
        st.write(f"⬆️ Given: {player.get('donations', 0)}")
    with col4:
        st.write(f"⬇️ Received: {player.get('donationsReceived', 0)}")
    
    # Other stats in expanders
    with st.expander("League & Season Info"):
        league = player.get("league", {})
        if league:
            st.write(f"🏆 League: {league.get('name', 'None')}")
        
        st.write(f"🏆 Best Trophies: {player.get('bestTrophies', 0)}")
        st.write(f"🏆 Best Versus Trophies: {player.get('bestVersusTrophies', 0)}")
    
    with st.expander("Heroes"):
        heroes = player.get("heroes", [])
        if heroes:
            for hero in heroes:
                st.write(f"{hero.get('name', 'Unknown')}: Level {hero.get('level', 0)}")
        else:
            st.write("No hero information available")
    
    with st.expander("Full JSON Data"):
        st.json(player)

if __name__ == "__main__":
    run()