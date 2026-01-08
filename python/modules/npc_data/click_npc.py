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

def click_closest_npc(ids_or_name, option=None, max_attempts=3):
    """
    Click the closest NPC.
    
    Args:
        ids_or_name: Either a list of int IDs OR a single string name (case-insensitive partial match allowed)
        option: Menu option to select (e.g., 'Attack', 'Escort')
        max_attempts: Retries for the actual click
    
    Returns:
        bool: Success
    """
    player_x, player_y, player_z = get_player_position()
    if player_x == 0 and player_y == 0:
        print("Invalid player position.")
        return False
    
    all_npc_data = npc(tile=True, middle_point=True)

    print(all_npc_data)
    if not all_npc_data or 'data' not in all_npc_data:
        print("Failed to fetch NPC data.")
        return False
        
    npcs = all_npc_data['data']
    candidates = []
    
    if isinstance(ids_or_name, str):
        # Name-based search (case-insensitive, partial match)
        name_lower = ids_or_name.lower()
        for n in npcs:
            npc_name = n.get('name', '')
            if npc_name and name_lower in npc_name.lower():
                tile = n.get('tile', {})
                nx = tile.get('x', 0)
                ny = tile.get('y', 0)
                nz = tile.get('z', 0)
                if nx != 0 and ny != 0:
                    dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                    candidates.append((dist, n['id'], n))  # Store dist, id, full npc dict
                    print(f"Found '{npc_name}' (ID {n['id']}) at distance {dist:.2f}")
    
    elif isinstance(ids_or_name, list):
        # ID list search
        id_set = set(ids_or_name)
        for n in npcs:
            if n.get('id') in id_set:
                tile = n.get('tile', {})
                nx = tile.get('x', 0)
                ny = tile.get('y', 0)
                nz = tile.get('z', 0)
                if nx != 0 and ny != 0:
                    dist = math.sqrt((nx - player_x)**2 + (ny - player_y)**2 + (nz - player_z)**2)
                    candidates.append((dist, n['id'], n))
                    print(f"Found NPC ID {n['id']} at distance {dist:.2f}")
    
    else:
        print("ids_or_name must be a list of IDs or a string name.")
        return False
    
    if not candidates:
        print("No matching NPCs found.")
        return False
    
    # Sort by distance and pick closest
    candidates.sort(key=lambda c: c[0])
    closest_dist, closest_id, closest_npc = candidates[0]
    closest_name = closest_npc.get('name', 'Unknown')
    print(f"Selecting closest NPC: '{closest_name}' (ID {closest_id}) at distance {closest_dist:.2f}")
    
    # Reuse click_npc logic but use the full npc dict for coordinates
    middle_point = closest_npc.get('middle_point', {})
    x = middle_point.get('x', 0)
    y = middle_point.get('y', 0)
    if x == 0 or y == 0:
        print("Invalid screen coordinates for closest NPC.")
        return False
    
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt} to select '{option}' on closest NPC...")
        if option:
            success = select_menu_option(x, y, option)
            if success:
                print(f"Successfully selected '{option}' on '{closest_name}'.")
                return True
        else:
            print(f"Basic click on closest NPC '{closest_name}'.")
            return True  # Assume success
    
    print(f"Failed after {max_attempts} attempts.")
    return False



# click_closest_npc('undead lumberjack', 'attack')

# escort_ids = [1566, 1567, 1578, 1577]
# print(click_closest_npc(escort_ids, 'Escort'))

# Example usage
# print(click_npc('Dominic Onion', 'Dream'))
# click_npc(1567, 'Escort')
