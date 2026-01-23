"""
Utils - Yardımcı fonksiyonlar
Şampiyon verileri, resim URL'leri ve caching
"""

import requests
import threading
from functools import lru_cache

# Cache for champion data
_champion_cache = {
    'version': None,
    'champion_map': {},
    'champion_list': [],
    'lock': threading.Lock()
}

def get_latest_version():
    """
    Fetches the latest League of Legends version from DataDragon.
    """
    try:
        response = requests.get("https://ddragon.leagueoflegends.com/api/versions.json", timeout=10)
        if response.status_code == 200:
            return response.json()[0]
    except Exception as e:
        print(f"Error fetching version: {e}")
    return None

def normalize_name(name):
    """
    Normalizes a champion name by removing spaces and special characters, and converting to lowercase.
    e.g. "Dr. Mundo" -> "drmundo", "Cho'Gath" -> "chogath"
    """
    return "".join(c for c in name if c.isalnum()).lower()

def get_champion_map(version):
    """
    Fetches the champion list and returns a dictionary mapping normalized champion names to their IDs.
    Also caches the full champion list for autocomplete.
    """
    with _champion_cache['lock']:
        # Return cached if version matches
        if _champion_cache['version'] == version and _champion_cache['champion_map']:
            return _champion_cache['champion_map']
    
    try:
        url = f"https://ddragon.leagueoflegends.com/cdn/{version}/data/en_US/champion.json"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()['data']
            
            champion_map = {}
            champion_list = []
            
            for champ_id, champ_data in data.items():
                name = champ_data['name']
                key = champ_data['key']
                normalized = normalize_name(name)
                
                champion_map[normalized] = key
                champion_list.append({
                    'id': champ_id,
                    'key': key,
                    'name': name,
                    'normalized': normalized
                })
            
            # Sort by name
            champion_list.sort(key=lambda x: x['name'])
            
            with _champion_cache['lock']:
                _champion_cache['version'] = version
                _champion_cache['champion_map'] = champion_map
                _champion_cache['champion_list'] = champion_list
            
            return champion_map
    except Exception as e:
        print(f"Error fetching champions: {e}")
    return {}

def get_champion_list():
    """
    Returns the cached list of all champions with full info.
    Returns list of dicts: [{'id': 'Aatrox', 'key': '266', 'name': 'Aatrox', 'normalized': 'aatrox'}, ...]
    """
    with _champion_cache['lock']:
        return list(_champion_cache['champion_list'])

def get_champion_names():
    """
    Returns a simple list of champion names for autocomplete.
    """
    with _champion_cache['lock']:
        return [c['name'] for c in _champion_cache['champion_list']]

def get_champion_image_url(champion_id: str, version: str = None) -> str:
    """
    Returns the URL for a champion's square icon.
    champion_id: The champion's ID (e.g., 'Aatrox', 'LeeSin')
    """
    if version is None:
        version = _champion_cache.get('version', '14.1.1')
    return f"https://ddragon.leagueoflegends.com/cdn/{version}/img/champion/{champion_id}.png"

def get_champion_splash_url(champion_id: str, skin_num: int = 0) -> str:
    """
    Returns the URL for a champion's splash art.
    """
    return f"https://ddragon.leagueoflegends.com/cdn/img/champion/splash/{champion_id}_{skin_num}.jpg"

def get_champion_loading_url(champion_id: str, skin_num: int = 0) -> str:
    """
    Returns the URL for a champion's loading screen art.
    """
    return f"https://ddragon.leagueoflegends.com/cdn/img/champion/loading/{champion_id}_{skin_num}.jpg"

def find_champion_by_name(name: str) -> dict:
    """
    Find a champion by partial name match.
    Returns the best matching champion dict or None.
    """
    if not name:
        return None
    
    name_lower = name.lower()
    normalized_search = normalize_name(name)
    
    champions = get_champion_list()
    
    # Exact normalized match first
    for champ in champions:
        if champ['normalized'] == normalized_search:
            return champ
    
    # Partial match
    for champ in champions:
        if normalized_search in champ['normalized']:
            return champ
        if name_lower in champ['name'].lower():
            return champ
    
    return None

def search_champions(query: str, limit: int = 10) -> list:
    """
    Search champions by partial name match.
    Returns list of matching champion dicts.
    """
    if not query:
        return get_champion_list()[:limit]
    
    query_lower = query.lower()
    normalized_query = normalize_name(query)
    
    champions = get_champion_list()
    matches = []
    
    # Prioritize starts-with matches
    for champ in champions:
        if champ['normalized'].startswith(normalized_query):
            matches.append(champ)
    
    # Then contains matches
    for champ in champions:
        if champ not in matches:
            if normalized_query in champ['normalized']:
                matches.append(champ)
    
    return matches[:limit]

def get_cached_version():
    """Returns the currently cached version"""
    return _champion_cache.get('version')
