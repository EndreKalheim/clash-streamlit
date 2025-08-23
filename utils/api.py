import requests
import concurrent.futures
import time
from itertools import product
import json
from parameters import API_KEY, THREADS, BASE_URL  # Import BASE_URL instead of hardcoding URLs
import streamlit as st  # Add this import at the top

session = requests.Session()

# Clan name generation prefixes and suffixes
PREFIXES = [
    "The", "Clan", "War", "King", "Queen", "Legend", "Elite", "Dark", "Shadow", "Dragon", "Knight",
    "Empire", "Reign", "Wolf", "Tiger", "Hunter", "Phoenix", "Iron", "Steel", "Lion", "Storm", "Flame",
    "Gold", "Night", "Epic", "Royal", "Blaze", "Rune", "Bastion", "Legion", "Vortex", "Strike", "Arcane",
    "Ace", "Ark", "Bar", "Fox", "Ice", "Jet", "Lux", "Neo", "Pax", "Rex", "Tor", "Vox", "Zip", "Brave",
    "Silent", "Strong", "Wise", "Bear", "Hawk", "Raven", "Eagle", "Thunder", "Glory", "Chaos", "Valor",
    "Fury", "Savage", "Mystic", "Crimson", "Rogue", "Omega", "Vengeance", "Titan", "Rebel", "Phantom",
    "Celestial", "Nova", "Infinity", "Gladiator", "Merciless", "Rampage", "Outlaw", "Warlock", "Cursed", "Divine",
    "Clash", "Spy", "Noble", "Diamond", "Sapphire", "Viper", "Chrome", "Mercury", "Neon", "Argon", "Xenon"
]

SUFFIXES = [
    "Legion", "Empire", "Knights", "Reign", "Warriors", "Clan", "Force", "Guardians", "Hunters", "Flames",
    "Wolves", "Eagles", "Dragons", "Phoenix", "Titans", "Lions", "Blaze", "Inferno", "Storm", "Vortex", "Strike",
    "Fury", "Riders", "Rangers", "Slayers", "Crusaders", "Vikings", "Marauders", "Assassins", "Soldiers", "Brothers",
    "King", "Spy", "Clash", "Noble", "Crystal", "Quartz", "Steel", "Mercury", "Copper", "Bronze", "Platinum"
]

headers = {"Authorization": f"Bearer {API_KEY}"}

class ClashAPI:
    """Centralized API client for Clash of Clans"""
    
    def __init__(self):
        self.headers = {"Authorization": f"Bearer {API_KEY}"}
        self.base_url = BASE_URL

    def make_request(self, endpoint, params=None):
        """Make a request to the Clash API with proper error handling"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"

        try:
            response = requests.get(url, headers=self.headers, params=params)
            # Log the request for debugging
            if hasattr(st, 'session_state') and "api_calls" in st.session_state:
                st.session_state.api_calls.append({
                    "url": url,
                    "status_code": response.status_code,
                    "success": response.status_code == 200,
                    "response": response.text[:100] + "..." if len(response.text) > 100 else response.text
                })
            
            response.raise_for_status()
            return response.json()
        except Exception as e:
            if hasattr(st, 'session_state') and "api_calls" in st.session_state:
                st.session_state.api_calls.append({
                    "url": url,
                    "status_code": "Error",
                    "success": False,
                    "response": str(e)
                })
            # Return error object instead of raising
            return {"error": True, "message": str(e), "url": url}

# Create an instance to use throughout the app
api_client = ClashAPI()

def get_clan(clan_tag):
    """Get information about a specific clan"""
    return api_client.make_request(f"clans/{clan_tag.replace('#', '%23')}")

def get_player(player_tag):
    """Get information about a specific player"""
    return api_client.make_request(f"players/{player_tag.replace('#', '%23')}")

def search_clans(params):
    """Search for clans with the given parameters"""
    return api_client.make_request("clans", params)

# Add more detailed error handling for debugging
def search_clans_with_retry(params, max_retries=3):
    """Search for clans with retry logic and better error reporting"""
    for attempt in range(max_retries):
        result = api_client.make_request("clans", params)
        if not result.get("error"):
            return result
        elif attempt < max_retries - 1:
            time.sleep(1)  # Wait before retrying
            continue
    return result  # Return the last error result

def get_headers(api_key=API_KEY):
    """Create headers with the provided API key."""
    return {"Authorization": f"Bearer {api_key}", "Accept": "application/json"}

def generate_optimized_search_terms(prefixes=None, suffixes=None):
    """Generate search terms from prefixes and suffixes."""
    if prefixes is None:
        prefixes = PREFIXES
    if suffixes is None:
        suffixes = SUFFIXES
        
    terms = set(prefixes + suffixes)
    terms.update(f"{prefix} {suffix}" for prefix, suffix in product(prefixes, suffixes))
    return list(terms)

def get_clan_members(clan_tag, api_key=API_KEY):
    """Get members of a clan by clan tag."""
    headers = get_headers(api_key)
    url = f"{BASE_URL}/clans/{clan_tag.replace('#', '%23')}"
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 429:  # Rate limit
                time.sleep(1)
                retry_count += 1
                continue
            elif response.status_code == 200:
                return response.json().get("memberList", [])
            else:
                return []
        except Exception:
            retry_count += 1
            time.sleep(1)
    
    return []  # Failed after retries

def get_player_info(player_tag, api_key=API_KEY):
    """Get detailed information about a player."""
    headers = get_headers(api_key)
    url = f"{BASE_URL}/players/{player_tag.replace('#', '%23')}"
    
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            response = session.get(url, headers=headers)
            if response.status_code == 429:  # Rate limit
                time.sleep(1)
                retry_count += 1
                continue
            elif response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception:
            retry_count += 1
            time.sleep(1)
    
    return None  # Failed after retries

# Alias for compatibility
get_player_details = get_player_info

def get_clans_by_name_deduplicated(name, seen_tags, api_key=API_KEY, min_members=10, max_members=200):
    """Search for clans by name, avoiding duplicates."""
    headers = get_headers(api_key)
    url = f"{BASE_URL}/clans"  # Use BASE_URL instead of hardcoding
    params = {"name": name, "minMembers": min_members, "maxMembers": max_members, "limit": 200}
    
    try:
        response = session.get(url, headers=headers, params=params)
        response.raise_for_status()
        clans = response.json().get("items", [])
        unique_clans = [clan for clan in clans if clan["tag"] not in seen_tags]
        for clan in unique_clans:
            seen_tags.add(clan["tag"])
        return unique_clans
    except requests.exceptions.RequestException:
        return []

def filter_league_clans(clans, league_filter):
    """Filter clans by league name."""
    if not league_filter:
        return clans
    return [clan for clan in clans if league_filter.lower() in clan.get("warLeague", {}).get("name", "").lower()]

def filter_language_clans(clans, language_code):
    """Filter clans by chat language."""
    if not language_code:
        return clans
    return [clan for clan in clans if clan.get("chatLanguage", {}).get("languageCode", "").lower() == language_code.lower()]

# New optimized search function that processes players as clans are found
def search_players_optimized(min_townhall=16, min_attack_wins=40, min_war_stars=500, 
                           min_trophies=4500, language_filter="en", league_filter="Crystal", 
                           exclude_roles=None, threads=THREADS, min_members=10, max_members=200,
                           max_clans=100, api_key=API_KEY, progress_callback=None, seen_clan_tags=None):
    """
    Optimized search that processes players as clans are found.
    """
    if exclude_roles is None:
        exclude_roles = ["leader"]
    
    # Initialize seen_clan_tags if not provided
    if seen_clan_tags is None:
        seen_clan_tags = set()
    
    search_terms = generate_optimized_search_terms()
    found_players = []
    processed_clans = 0
    
    # Create a thread pool for player processing that we'll use throughout
    player_executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads)
    player_futures = {}
    
    # Create a thread pool for clan searching
    clan_search_executor = concurrent.futures.ThreadPoolExecutor(max_workers=threads // 2)
    clan_futures = {}
    
    # Start searching for clans - limit to fewer search terms initially
    initial_terms = search_terms[:10]  # Start with fewer terms to get results faster
    remaining_terms = search_terms[10:]
    
    # Function to process a clan and submit player requests
    def process_clan(clan):
        nonlocal processed_clans
        clan_tag = clan["tag"]
        
        if progress_callback:
            progress_callback("clan_found", clan)
            progress_callback("clan_processing", clan)  # Add new progress type
            
        members = get_clan_members(clan_tag, api_key)
        processed_clans += 1
        
        # Filter potential players
        potential_players = [
            member["tag"] for member in members
            if member.get("townHallLevel", 0) >= min_townhall and 
               member.get("role", "") not in exclude_roles
        ]
        
        # Submit player requests
        for player_tag in potential_players:
            future = player_executor.submit(get_player_info, player_tag, api_key)
            player_futures[future] = player_tag
    
    # Submit initial clan search requests
    for term in initial_terms:
        future = clan_search_executor.submit(
            get_clans_by_name_deduplicated, 
            term, 
            seen_clan_tags, 
            api_key, 
            min_members, 
            max_members
        )
        clan_futures[future] = term
    
    # Track how many clans we've found and processed
    clans_found = 0
    clans_needed = max_clans
    
    # Process clans and players in a pipeline fashion
    while clans_found < clans_needed and (clan_futures or player_futures):
        # First, check for completed clan searches and process any found clans
        if clan_futures:
            # Wait for at least one clan search to complete but don't block indefinitely
            done_clan_futures, clan_futures = concurrent.futures.wait(
                clan_futures, 
                timeout=0.1,
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done_clan_futures:
                clans = future.result()
                term = clan_futures.pop(future, None)
                
                # Apply filters
                if language_filter:
                    clans = filter_language_clans(clans, language_filter)
                if league_filter:
                    clans = filter_league_clans(clans, league_filter)
                
                # Process each clan found
                for clan in clans:
                    clans_found += 1
                    # Immediately process this clan to get its players
                    process_clan(clan)
                    
                    if clans_found >= clans_needed:
                        break
                
                # If we need more clans and have more terms, submit another search
                if clans_found < clans_needed and remaining_terms:
                    next_term = remaining_terms.pop(0)
                    future = clan_search_executor.submit(
                        get_clans_by_name_deduplicated, 
                        next_term, 
                        seen_clan_tags, 
                        api_key, 
                        min_members, 
                        max_members
                    )
                    clan_futures[future] = next_term
        
        # Then, check for completed player info requests
        if player_futures:
            # Wait for at least one player but don't block indefinitely
            done_player_futures, player_futures = concurrent.futures.wait(
                player_futures, 
                timeout=0.1,
                return_when=concurrent.futures.FIRST_COMPLETED
            )
            
            for future in done_player_futures:
                player_info = future.result()
                player_tag = player_futures.pop(future, None)
                
                if player_info and player_info.get("attackWins", 0) >= min_attack_wins \
                   and player_info.get("warStars", 0) >= min_war_stars \
                   and player_info.get("trophies", 0) >= min_trophies:
                    found_players.append(player_info)
                    if progress_callback:
                        progress_callback("player_found", player_info)
    
    # Shutdown executors cleanly
    clan_search_executor.shutdown(wait=False)
    player_executor.shutdown()
    
    return found_players

# Legacy function kept for backward compatibility
def search_players(api_key=API_KEY, min_townhall=16, min_attack_wins=40, min_war_stars=500, 
                 min_trophies=4500, language_filter="en", league_filter="Crystal", 
                 exclude_roles=None, threads=THREADS, min_members=10, max_members=200):
    """Wrapper function that combines clan search and player search."""
    # Get clans first
    clans = get_all_clans(
        api_key=api_key,
        threads=threads,
        min_members=min_members,
        max_members=max_members,
        language_filter=language_filter,
        league_filter=league_filter
    )
    
    # Then find active players in those clans
    players = find_active_players(
        clans=clans,
        api_key=api_key,
        threads=threads,
        min_townhall=min_townhall,
        min_attack_wins=min_attack_wins,
        min_war_stars=min_war_stars,
        min_trophies=min_trophies,
        exclude_roles=exclude_roles
    )
    
    return clans, players

# Legacy functions kept for backward compatibility
def get_all_clans(api_key=API_KEY, threads=THREADS, min_members=10, max_members=200, language_filter=None, league_filter=None):
    """Search for clans using a list of common clan name terms."""
    search_terms = generate_optimized_search_terms()
    all_clans = []
    seen_tags = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(
                get_clans_by_name_deduplicated, 
                term, 
                seen_tags, 
                api_key, 
                min_members, 
                max_members
            ): term for term in search_terms
        }
        
        for future in concurrent.futures.as_completed(futures):
            clans = future.result()
            all_clans.extend(clans)

    if language_filter:
        all_clans = filter_language_clans(all_clans, language_filter)
    
    if league_filter:
        all_clans = filter_league_clans(all_clans, league_filter)

    return all_clans

def find_active_players(clans, api_key=API_KEY, threads=THREADS, min_townhall=16, min_attack_wins=40, 
                        min_war_stars=500, min_trophies=4500, exclude_roles=None):
    """Find active players from a list of clans that meet certain criteria."""
    if exclude_roles is None:
        exclude_roles = ["leader"]
        
    all_active_players = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as executor:
        for clan in clans:
            clan_tag = clan["tag"]
            members = get_clan_members(clan_tag, api_key)

            potential_players = [
                member["tag"] for member in members
                if member.get("townHallLevel", 0) >= min_townhall and 
                   member.get("role", "") not in exclude_roles
            ]

            future_to_tag = {
                executor.submit(get_player_info, player_tag, api_key): player_tag
                for player_tag in potential_players
            }

            for future in concurrent.futures.as_completed(future_to_tag):
                player_info = future.result()
                if player_info and player_info.get("attackWins", 0) >= min_attack_wins \
                   and player_info.get("warStars", 0) >= min_war_stars \
                   and player_info.get("trophies", 0) >= min_trophies:
                    all_active_players.append(player_info)

    return all_active_players