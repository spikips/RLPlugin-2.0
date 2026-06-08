import math
import time

from modules.core.plugin_client import npc, player
from modules.core.window_utils import runelite_window

rl_x, rl_y = runelite_window(0, 0)

def check_npc_animation(animation_id: int, npc_name: str, tile_radius: int = 10) -> bool:
    """
    Checks if any NPC of the given name within the tile radius has the specified animation ID.
    
    Args:
        animation_id (int): The animation ID to check for.
        npc_name (str): Name of the NPCs to check.
        tile_radius (int): Maximum distance in tiles to consider NPCs (default: 10).
    
    Returns:
        bool: True if any NPC has the matching animation, False otherwise.
    """
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player data.")
        return False

    p_loc = player_data['data']['location']
    p_x = p_loc['x']
    p_y = p_loc['y']

    npc_data = npc(name=npc_name, tile=True, middle_point=True)
    if not npc_data or 'data' not in npc_data or not npc_data['data']:
        # Avoid spamming "No xxx found." in tight loops (e.g. tail_mon every tick)
        # Callers that want debug can handle themselves.
        return False

    for n in npc_data['data']:
        if 'tile' not in n or 'middle_point' not in n:
            continue
        n_tile = n['tile']
        dx = abs(n_tile['x'] - p_x)
        dy = abs(n_tile['y'] - p_y)
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= tile_radius and n.get('animation') == animation_id:
            return True

    return False

# while True:
#     is_dying = check_npc_animation(4659, 'moss giant')
#     print(is_dying)
#     time.sleep(0.6)