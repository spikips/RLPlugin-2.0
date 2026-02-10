from typing import Optional, Tuple, List, Dict, Any

from modules.core.plugin_client import fetch_object, player
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

def get_objects(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> List[Dict[str, Any]]:
    """
    Fetch local objects, filtered by identifier and action, around player or specified tile.
    - If no identifier, returns all within radius that match action.
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

    fetch_radius = radius if tile is None else 20  # Broader fetch for filtering if tile given
    obj_data = fetch_object(object_identifier, action, tile_x=center_tile[0] if tile else None, tile_y=center_tile[1] if tile else None, radius=fetch_radius)
    if obj_data is None or 'data' not in obj_data:
        print(f"No objects found for identifier '{object_identifier}' with action '{action}'.")
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

def get_closest_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20, disregard_canvas: bool = False) -> Optional[Dict[str, Any]]:
    """
    Get the closest matching object.
    - Prioritizes tile proximity for precision in crowded areas.
    - By default (disregard_canvas=False): Filters to objects whose middle_point is within canvas bounds
      (x: CANVAS_X_MIN to CANVAS_X_MAX, y: CANVAS_Y_MIN to CANVAS_Y_MAX) to ensure clickability on-screen.
    - If disregard_canvas=True: Ignores canvas bounds and considers all objects with a middle_point
      (useful for off-screen objects or when you plan to move/camera first).
    """
    objs = get_objects(object_identifier, action, tile, radius)
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

    # Log all objects' canvas coordinates for debugging (only if middle_point exists)
    for o in objs:
        if 'middle_point' in o:
            canvas_x = o['middle_point']['x']
            canvas_y = o['middle_point']['y']
            on_canvas = (CANVAS_X_MIN <= canvas_x <= CANVAS_X_MAX and
                         CANVAS_Y_MIN <= canvas_y <= CANVAS_Y_MAX)
            status = " (on canvas)" if on_canvas else " (off canvas)"
            print(f"Found object '{object_identifier}' with action '{action}' at canvas ({canvas_x}, {canvas_y}){status}")

    # Filter objects: always require middle_point (needed for clicking)
    candidate_objs = [o for o in objs if 'middle_point' in o]

    if disregard_canvas:
        valid_objs = candidate_objs  # Consider all, even off-screen
        print(f"disregard_canvas=True: Considering {len(valid_objs)} object(s) (ignoring canvas bounds)")
    else:
        valid_objs = [
            o for o in candidate_objs
            if CANVAS_X_MIN <= o['middle_point']['x'] <= CANVAS_X_MAX and
               CANVAS_Y_MIN <= o['middle_point']['y'] <= CANVAS_Y_MAX
        ]
        print(f"disregard_canvas=False: Considering {len(valid_objs)} object(s) within canvas bounds")

    if not valid_objs:
        reason = "off-screen (outside canvas bounds)" if not disregard_canvas else "no middle_point available"
        print(f"No valid objects found for identifier '{object_identifier}' with action '{action}' ({reason}).")
        return None

    # Return the closest by tile distance
    closest = min(valid_objs, key=lambda o: tile_distance((o['tile']['x'], o['tile']['y']), center_tile))
    final_canvas_x = closest['middle_point']['x']
    final_canvas_y = closest['middle_point']['y']
    on_canvas = (CANVAS_X_MIN <= final_canvas_x <= CANVAS_X_MAX and
                 CANVAS_Y_MIN <= final_canvas_y <= CANVAS_Y_MAX)
    print(f"Selected closest object at tile ({closest['tile']['x']}, {closest['tile']['y']}) "
          f"with canvas middle_point ({final_canvas_x}, {final_canvas_y}){' (on canvas)' if on_canvas else ' (off canvas)'}")
    return closest

def check_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> bool:
    """
    Check if a matching object exists within the specified radius.
    - Returns True if found within canvas bounds, False otherwise.
    - View: Non-invasive check for object presence before attempting interaction.
    """
    obj = get_closest_object(object_identifier, action, tile, radius)
    return obj is not None

def click_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> bool:
    """
    Click a local object with specified action using select_menu_option.
    - Flexible: ID or name; player-centered if no tile.
    - Views: Mimics human-like interaction by right-clicking, checking options, then clicking.
    - Ensures clicks are within canvas bounds (x: 4-512, y: 4-334).
    """
    focus_runelite_window()  # Ensure window focus for inputs

    obj = get_closest_object(object_identifier, action, tile, radius)

    if obj is None or 'middle_point' not in obj:
        print(f"No object found for identifier '{object_identifier}' with action '{action}' within radius {radius} or canvas bounds.")
        return False

    mp = obj['middle_point']
    result = select_menu_option(mp['x'], mp['y'], action)
    return result is not None

def use_on_object(object_identifier: str, action: str, use_option: str, tile: Optional[Tuple[int, int]] = None, radius: int = 6) -> bool:
    """
    Locate a local object with the specified base action available, then select a different menu option.
    - Finds closest object matching identifier and having `action` in its actions (e.g., for hover-dependent visibility).
    - Logs: "Found object '13834' with action 'Inspect' at canvas (281, 172)".
    - Then right-clicks and selects `use_option` (e.g., 'Use Item -> Inspect').
    - Addresses hover-dependent actions: Uses `action` for filtering, `use_option` for final selection.
    - Bigger picture: Handles scenarios where base actions differ from hovered/interactive ones, ensuring precise selection.
    """
    focus_runelite_window()  # Ensure window focus for inputs

    obj = get_closest_object(object_identifier, action, tile, radius)

    if obj is None or 'middle_point' not in obj:
        print(f"No object found for identifier '{object_identifier}' with action '{action}' within radius {radius} or canvas bounds.")
        return False

    mp = obj['middle_point']
    print(f"Found object '{object_identifier}' with action '{action}' at canvas ({mp['x']}, {mp['y']})")

    # Optionally log available actions if present in the object data
    if 'actions' in obj:
        print(f"Available actions: {', '.join(obj['actions'])}")

    # Perform the right-click and select the specified use_option
    result = select_menu_option(mp['x'], mp['y'], use_option)
    return result is not None

# while True:
#     print(check_object('1524', 'open'))