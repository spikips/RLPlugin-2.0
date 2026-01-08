import time
import math

from modules.core.plugin_client import npc, player

def wait_for_npc_animation(animation_id: int, npc_name: str, tile_radius: int = 10, timeout: float = 30.0, check_interval: float = 0.5) -> bool:
    """
    Waits until any NPC of the given name within the tile radius enters the specified animation ID.
    
    Args:
        animation_id (int): The animation ID to wait for.
        npc_name (str): Name of the NPCs to monitor.
        tile_radius (int): Maximum distance in tiles to consider NPCs (default: 10).
        timeout (float): Maximum time in seconds to wait (default: 30.0).
        check_interval (float): Time in seconds between checks (default: 0.5).
    
    Returns:
        bool: True if the animation is detected within timeout, False otherwise.
    """
    start_time = time.time()
    
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player data.")
        return False

    p_loc = player_data['data']['location']
    p_x = p_loc['x']
    p_y = p_loc['y']

    while time.time() - start_time < timeout:
        npc_data = npc(name=npc_name, tile=True, middle_point=True)
        if not npc_data or 'data' not in npc_data or not npc_data['data']:
            print(f"No {npc_name} found.")
            time.sleep(check_interval)
            continue

        for n in npc_data['data']:
            if 'tile' not in n or 'middle_point' not in n:
                continue
            n_tile = n['tile']
            dx = abs(n_tile['x'] - p_x)
            dy = abs(n_tile['y'] - p_y)
            dist = math.sqrt(dx**2 + dy**2)
            if dist <= tile_radius and n.get('animation') == animation_id:
                return True

        time.sleep(check_interval)

    print(f"Timeout reached without detecting animation {animation_id} for {npc_name}.")
    return False

# Example usage
waited = wait_for_npc_animation(4659, 'moss giant')
print(waited)