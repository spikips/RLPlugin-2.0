from typing import Optional, Tuple, List, Dict, Any

from modules.core.plugin_client import game_object as fetch_game_object, player
from modules.core.window_utils import focus_runelite_window
from modules.utils.select_menu_option import select_menu_option

# Canvas bounds for valid clicks
CANVAS_X_MIN = 4
CANVAS_X_MAX = 512
CANVAS_Y_MIN = 4
CANVAS_Y_MAX = 334

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
        if player_data is None or 'data' not in player_data or 'location' not in player_data['data']:
            print("Failed to retrieve player location data.")
            return []
        center_tile = (player_data['data']['location']['x'], player_data['data']['location']['y'])
    else:
        center_tile = tile

    fetch_radius = radius if tile is None else 10  # Broader fetch for filtering if tile given
    obj_data = fetch_game_object(object=object_identifier, tile_radius=fetch_radius, middle_point=False)
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
    Get the closest matching game object within canvas bounds (x: 4-512, y: 4-334).
    - Prioritizes proximity for precision in crowded areas.
    - View: Reduces errors in multi-object scenarios; ensures clicks are within valid canvas.
    """
    objs = get_game_objects(object_identifier, tile, radius)
    if not objs:
        return None

    if tile is None:
        player_data = player(location=True)
        if player_data is None or 'data' not in player_data or 'location' not in player_data['data']:
            print("Failed to retrieve player location data for closest object.")
            return None
        center_tile = (player_data['data']['location']['x'], player_data['data']['location']['y'])
    else:
        center_tile = tile

    # Log all objects' canvas coordinates for debugging
    for o in objs:
        if 'middle_point' in o:
            print(f"Found game object '{object_identifier}' at canvas ({o['middle_point']['x']}, {o['middle_point']['y']})")
    
    # Filter objects by canvas bounds
    valid_objs = [
        o for o in objs
        if 'middle_point' in o and
        CANVAS_X_MIN <= o['middle_point']['x'] <= CANVAS_X_MAX and
        CANVAS_Y_MIN <= o['middle_point']['y'] <= CANVAS_Y_MAX
    ]
    if not valid_objs:
        print(f"No game objects found for identifier '{object_identifier}' within canvas bounds.")
        return None

    return min(valid_objs, key=lambda o: tile_distance((o['tile']['x'], o['tile']['y']), center_tile))

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
    - Ensures clicks are within canvas bounds (x: 4-512, y: 4-334).
    """
    focus_runelite_window()  # Ensure window focus for inputs

    obj = get_closest_game_object(object_identifier, tile, radius)

    if obj is None or 'middle_point' not in obj:
        print(f"No game object found for identifier '{object_identifier}' within radius {radius} or canvas bounds.")
        return False

    mp = obj['middle_point']
    result = select_menu_option(mp['x'], mp['y'], action)
    return result is not None