from typing import Optional, Tuple, List, Dict, Any

from modules.core.plugin_client import game_object as fetch_game_object, player
from modules.core.window_utils import focus_runelite_window
from modules.utils.select_menu_option import select_menu_option

def tile_distance(t1: Tuple[int, int], t2: Tuple[int, int]) -> int:
    """Calculate Manhattan distance between two tiles for efficient filtering."""
    return abs(t1[0] - t2[0]) + abs(t1[1] - t2[1])

def get_game_objects(object_identifier: str = "", tile: Optional[Tuple[int, int]] = None, radius: int = 10) -> List[Dict[str, Any]]:
    """
    Fetch game objects, optionally filtered by identifier, around player or specified tile.
    - If no identifier, returns all within radius.
    - Defaults to player-centered search; uses broader fetch if tile specified, then filters.
    - Helps understand object distribution: player view vs. targeted area for bot pathing.
    """
    if tile is None:
        player_data = player(location=True)
        if player_data is None or 'data' not in player_data or 'tile' not in player_data['data']:
            print("Failed to retrieve player tile data.")
            return []
        center_tile = (player_data['data']['tile']['x'], player_data['data']['tile']['y'])
    else:
        center_tile = tile

    fetch_radius = radius if tile is None else radius + 10  # Broader fetch for filtering if tile given
    obj_data = fetch_game_object(object=object_identifier, tile_radius=fetch_radius, middle_point=True)
    print(obj_data)
    if obj_data is None or 'data' not in obj_data:
        print(f"No game objects found for identifier '{object_identifier}'.")
        return []

    all_objs = obj_data['data']
    if tile is None:
        return all_objs

    filtered_objs = []
    for o in all_objs:
        if 'tile' not in o or 'x' not in o['tile'] or 'y' not in o['tile']:
            continue  # Skip objects with missing or malformed tile data
        obj_tile = (o['tile']['x'], o['tile']['y'])
        if tile_distance(obj_tile, center_tile) <= radius:
            filtered_objs.append(o)
    
    return filtered_objs

def get_closest_game_object(object_identifier: str = "", tile: Optional[Tuple[int, int]] = None, radius: int = 10) -> Optional[Dict[str, Any]]:
    """
    Get the closest matching game object.
    - Prioritizes proximity for precision in crowded areas.
    - View: Reduces errors in multi-object scenarios; bigger picture for bot decision-making.
    """
    objs = get_game_objects(object_identifier, tile, radius)
    if not objs:
        return None

    if tile is None:
        player_data = player(location=True)
        if player_data is None or 'data' not in player_data or 'tile' not in player_data['data']:
            print("Failed to retrieve player tile data for closest object.")
            return None
        center_tile = (player_data['data']['tile']['x'], player_data['data']['tile']['y'])
    else:
        center_tile = tile

    return min(objs, key=lambda o: tile_distance((o['tile']['x'], o['tile']['y']), center_tile))

def hover_gameobject(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 6) -> bool:
    """
    Hover over a game object's action in menu using select_menu_option.
    - Similar to click but no final click; useful for checks before commit.
    - Bigger picture: Enables non-committal inspections in bot logic flows.
    """
    focus_runelite_window()  # Ensure window focus for inputs

    obj = get_closest_game_object(object_identifier, tile, radius)
    if obj is None or 'middle_point' not in obj:
        print(f"No game object found for identifier '{object_identifier}' within radius {radius}.")
        return False

    mp = obj['middle_point']
    result = select_menu_option(mp['x'], mp['y'], action, hover_only=True)
    return result is not None

def click_gameobject(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 6) -> bool:
    """
    Click a game object with specified action using select_menu_option.
    - Flexible: ID or name; player-centered if no tile.
    - Views: Mimics human-like interaction by right-clicking, checking options, then clicking.
    """
    focus_runelite_window()  # Ensure window focus for inputs

    obj = get_closest_game_object(object_identifier, tile, radius)
    if obj is None or 'middle_point' not in obj:
        print(f"No game object found for identifier '{object_identifier}' within radius {radius}.")
        return False

    mp = obj['middle_point']
    print(f"Found game object '{object_identifier}' at canvas ({mp['x']}, {mp['y']})")
    result = select_menu_option(mp['x'], mp['y'], action)
    return result is not None

# click_gameobject('16962', 'examine', (2212, 3809), 5)
# click_gameobject('16962', 'examine ladder', (2212, 3809), 5)
