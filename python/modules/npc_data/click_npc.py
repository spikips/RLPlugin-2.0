from modules.core.plugin_client import npc, player
from modules.utils.select_menu_option import select_menu_option
import math

def get_player_position():
    """
    Retrieve the local player's world position.
    Returns: (x, y, z) or (0, 0, 0) if invalid.
    """
    player_data = player(location=True)
    if not player_data or 'data' not in player_data:
        print("Failed to fetch player data.")
        return 0, 0, 0
    
    location = player_data['data'].get('location', {})
    x = location.get('x', 0)
    y = location.get('y', 0)
    z = location.get('z', 0)
    return x, y, z

def click_npc(identifier, option=None, max_attempts=3):
    """
    Click a single NPC by ID (int) or exact name (str).
    """
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt} to click NPC {identifier}...")
        
        npc_data = npc(id=str(identifier) if isinstance(identifier, int) else "",
                       name=identifier if isinstance(identifier, str) else "",
                       tile=True, middle_point=True)
        if not npc_data or 'data' not in npc_data:
            print("No NPC data received.")
            continue
            
        target_npc = next((n for n in npc_data['data'] 
                          if (isinstance(identifier, int) and n.get('id') == identifier) or
                             (isinstance(identifier, str) and n.get('name') == identifier)), None)
        
        if not target_npc:
            print(f"NPC {identifier} not found.")
            continue
        
        middle_point = target_npc.get('middle_point', {})
        x = middle_point.get('x', 0)
        y = middle_point.get('y', 0)
        if x == 0 and y == 0:
            print("Invalid screen coordinates.")
            continue
        
        if option:
            success = select_menu_option(x, y, option)
            if success:
                print(f"Successfully selected '{option}' on NPC {identifier}.")
                return True
        else:
            print(f"Basic click on NPC {identifier} at ({x}, {y}).")
            return True  # Assume success for basic click
    
    print(f"Failed to click NPC {identifier} after {max_attempts} attempts.")
    return False

def click_closest_npc(ids_or_name, option=None, max_attempts=3, exact_name: bool = False):
    """
    Click the closest NPC whose middle_point (canvas coordinates) is valid and on-screen.
    - Canvas bounds: 1 <= x <= 515, 1 <= y <= 337 (standard RuneLite game view canvas size)
    - Only NPCs with canvas coordinates inside these bounds are considered candidates
    - Among valid candidates, picks the closest by world distance
    - Uses raw canvas_x, canvas_y directly in select_menu_option (exactly like your original working version)
    - No runelite_window conversion — this prevents any "way off" clicks
    - No move/left_click — uses select_menu_option for everything (including 'Attack')
    
    Args:
        ids_or_name: str (NPC name) or list[int] (NPC IDs)
        option (str, optional): Menu option to select (e.g., 'Attack')
        max_attempts (int): Number of click attempts
        exact_name (bool): If True and ids_or_name is str, requires exact name match (case-insensitive).
                           If False (default), allows partial match.
    """
    player_x, player_y, player_z = get_player_position()
    if player_x == 0 and player_y == 0:
        print("Invalid player position.")
        return False

    # Hardcoded canvas bounds (these are the raw coordinates the plugin gives for on-screen entities)
    CANVAS_MIN = 1
    CANVAS_MAX_X = 515
    CANVAS_MAX_Y = 337

    all_npc_data = npc(tile=True, middle_point=True)
    if not all_npc_data or 'data' not in all_npc_data:
        print("Failed to fetch NPC data.")
        return False
        
    npcs = all_npc_data['data']
    candidates = []
    
    if isinstance(ids_or_name, str):
        search_name_lower = ids_or_name.lower()
        for n in npcs:
            npc_name = n.get('name', '')
            if not npc_name:
                continue
                
            name_lower = npc_name.lower()
            matches = (exact_name and name_lower == search_name_lower) or \
                      (not exact_name and search_name_lower in name_lower)
            
            if matches:
                canvas_x = n.get('middle_point', {}).get('x', 0)
                canvas_y = n.get('middle_point', {}).get('y', 0)
                
                # Strict on-screen canvas bounds filter
                if not (CANVAS_MIN <= canvas_x <= CANVAS_MAX_X and CANVAS_MIN <= canvas_y <= CANVAS_MAX_Y):
                    print(f"Skipping '{npc_name}' (ID {n['id']}) - canvas ({canvas_x}, {canvas_y}) outside on-screen bounds")
                    continue
                
                tile = n.get('tile', {})
                nx = tile.get('x', 0)
                ny = tile.get('y', 0)
                nz = tile.get('z', 0)
                if nx == 0 or ny == 0:
                    continue
                
                dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                candidates.append((dist, n['id'], n, canvas_x, canvas_y))
                print(f"Valid on-screen candidate: '{npc_name}' (ID {n['id']}) dist {dist:.2f} canvas ({canvas_x}, {canvas_y})")
    
    elif isinstance(ids_or_name, list):
        id_set = set(ids_or_name)
        for n in npcs:
            if n.get('id') in id_set:
                canvas_x = n.get('middle_point', {}).get('x', 0)
                canvas_y = n.get('middle_point', {}).get('y', 0)
                
                if not (CANVAS_MIN <= canvas_x <= CANVAS_MAX_X and CANVAS_MIN <= canvas_y <= CANVAS_MAX_Y):
                    print(f"Skipping NPC ID {n['id']} - canvas outside bounds")
                    continue
                
                tile = n.get('tile', {})
                nx = tile.get('x', 0)
                ny = tile.get('y', 0)
                nz = tile.get('z', 0)
                if nx == 0 or ny == 0:
                    continue
                
                dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                candidates.append((dist, n['id'], n, canvas_x, canvas_y))
                print(f"Valid on-screen candidate: NPC ID {n['id']} dist {dist:.2f}")
    
    else:
        print("ids_or_name must be a list of IDs or a string name.")
        return False
    
    if not candidates:
        print("No matching on-screen NPCs found.")
        return False
    
    # Sort by world distance — closest first
    candidates.sort(key=lambda c: c[0])
    closest_dist, closest_id, closest_npc, canvas_x, canvas_y = candidates[0]
    closest_name = closest_npc.get('name', 'Unknown')
    print(f"Clicking closest on-screen NPC: '{closest_name}' (ID {closest_id}) dist {closest_dist:.2f} at canvas ({canvas_x}, {canvas_y})")
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt}/{max_attempts}...")
        if option:
            success = select_menu_option(canvas_x, canvas_y, option)
            if success:
                print(f"Success: '{option}' on '{closest_name}'")
                return True
        else:
            success = select_menu_option(canvas_x, canvas_y, None)
            if success:
                print(f"Basic left-click on '{closest_name}'")
                return True
    
    print("Failed after max attempts.")
    return False

# npcs = "Loar Shadow", "Loar Shade"
# for Nps in npcs:
#     success = click_closest_npc(Nps, 'Attack')  # Click closest 'Loar Shadow' or 'Loar Shade' and select 'Attack'
#     if success:
#         print(f"Successfully clicked closest NPC: {Nps}")
#         break

# click_closest_npc('undead lumberjack', 'attack')

# escort_ids = [1566, 1567, 1578, 1577]
# print(click_closest_npc(escort_ids, 'Escort'))

# Example usage
# print(click_npc('Dominic Onion', 'Dream'))
# click_npc(1567, 'Escort')