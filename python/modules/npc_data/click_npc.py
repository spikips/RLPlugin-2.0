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

def click_npc(identifier, option=None, max_attempts=3, fast=False):
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
            success = select_menu_option(x, y, option, fast=fast)
            if success:
                print(f"Successfully selected '{option}' on NPC {identifier}.")
                return True
        else:
            print(f"Basic click on NPC {identifier} at ({x}, {y}).")
            return True  # Assume success for basic click
    
    print(f"Failed to click NPC {identifier} after {max_attempts} attempts.")
    return False

def click_closest_npc(ids_or_name, option=None, max_attempts=3, exact_name: bool = False, fast: bool = False, tile_radius: int = None, quiet: bool = False):
    """
    Click the closest NPC whose middle_point (canvas coordinates) is valid and on-screen.
    
    NEW PROGRESSIVE RADIUS SEARCH (default behavior):
    - Starts with tile radius 5
    - If no valid NPC found → automatically tries radius 10
    - If still none → tries radius 20
    - Stops at the smallest radius that has at least one valid on-screen match
    - NPC data is fetched ONLY ONCE (big performance win)
    - Extremely fast even in crowded areas
    
    If you pass tile_radius=15 it will use ONLY that radius (backward compatible).
    
    Canvas bounds: 1 <= x <= 515, 1 <= y <= 337
    Uses raw canvas coordinates directly for clicks.
    """
    player_x, player_y, player_z = get_player_position()
    if player_x == 0 and player_y == 0:
        print("Invalid player position.")
        return False

    # Hardcoded canvas bounds (raw plugin coordinates)
    CANVAS_MIN = 1
    CANVAS_MAX_X = 515
    CANVAS_MAX_Y = 337

    # Fetch NPC data ONLY ONCE - this was the main performance bottleneck
    all_npc_data = npc(tile=True, middle_point=True)
    if not all_npc_data or 'data' not in all_npc_data:
        print("Failed to fetch NPC data.")
        return False
        
    npcs = all_npc_data['data']

    # Decide which radii to try
    if tile_radius is not None:
        radii_to_try = [tile_radius]
        print(f"Using fixed tile radius: {tile_radius}")
    else:
        radii_to_try = [5, 10, 20]
        if not quiet:
            print("Progressive radius search: trying 5 → 10 → 20")

    for radius in radii_to_try:
        if not quiet:
            print(f"Searching within radius {radius} tiles...")
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
                    
                    # Strict on-screen check
                    if not (CANVAS_MIN <= canvas_x <= CANVAS_MAX_X and CANVAS_MIN <= canvas_y <= CANVAS_MAX_Y):
                        continue
                    
                    tile = n.get('tile', {})
                    nx = tile.get('x', 0)
                    ny = tile.get('y', 0)
                    nz = tile.get('z', 0)
                    if nx == 0 or ny == 0:
                        continue
                    
                    dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                    
                    if dist > radius:
                        continue
                    
                    candidates.append((dist, n['id'], n, canvas_x, canvas_y))
        
        elif isinstance(ids_or_name, list):
            # Normalize to int for robust matching (data may have str or int IDs)
            id_set = {int(x) for x in ids_or_name if str(x).lstrip('-').isdigit()}
            for n in npcs:
                try:
                    nid = int(n.get('id', 0))
                except (ValueError, TypeError):
                    nid = None
                if nid is not None and nid in id_set:
                    canvas_x = n.get('middle_point', {}).get('x', 0)
                    canvas_y = n.get('middle_point', {}).get('y', 0)
                    
                    if not (CANVAS_MIN <= canvas_x <= CANVAS_MAX_X and CANVAS_MIN <= canvas_y <= CANVAS_MAX_Y):
                        continue
                    
                    tile = n.get('tile', {})
                    nx = tile.get('x', 0)
                    ny = tile.get('y', 0)
                    nz = tile.get('z', 0)
                    if nx == 0 or ny == 0:
                        continue
                    
                    dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                    
                    if dist > radius:
                        continue
                    
                    candidates.append((dist, nid, n, canvas_x, canvas_y))
        
        else:
            print("ids_or_name must be a list of IDs or a string name.")
            return False
        
        if candidates:
            # Found something in this radius - use the closest one
            candidates.sort(key=lambda c: c[0])
            closest_dist, closest_id, closest_npc, canvas_x, canvas_y = candidates[0]
            closest_name = closest_npc.get('name', 'Unknown')
            print(f"Found closest NPC within radius {radius}: '{closest_name}' (ID {closest_id}) dist {closest_dist:.2f} at canvas ({canvas_x}, {canvas_y})")
            
            # Try to click it
            for attempt in range(1, max_attempts + 1):
                print(f"Attempt {attempt}/{max_attempts}...")
                if option:
                    success = select_menu_option(canvas_x, canvas_y, option, fast=fast)
                    if success:
                        print(f"Success: '{option}' on '{closest_name}'")
                        return True
                else:
                    success = select_menu_option(canvas_x, canvas_y, None, fast=fast)
                    if success:
                        print(f"Basic left-click on '{closest_name}'")
                        return True
            
            print(f"Failed to click after {max_attempts} attempts (found NPC but click failed).")
            return False  # We found NPCs but couldn't click → no point escalating further
    
    # If we get here, none of the radii had any valid NPCs
    if not quiet:
        print(f"No matching on-screen NPC {ids_or_name} found in radii {radii_to_try}.")
    return False

# Example usage with new progressive search:
# click_closest_npc('Loar Shadow', 'Attack')                    # auto 5 → 10 → 20
# click_closest_npc('undead lumberjack', 'attack', tile_radius=15)  # force specific radius
# click_closest_npc([1566, 1567, 1578, 1577], 'Escort')         # works with ID lists too