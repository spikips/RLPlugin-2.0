import math
import time
import random

from modules.core.plugin_client import npc, player, interact_options 
from modules.core.mouse_control import move 
from modules.core.window_utils import runelite_window 

rl_x, rl_y = runelite_window(0, 0)

def attack(npc_name: str, tile_radius: int = 10, death_animation: int = None):
    """
    Attack the closest NPC of the given name within the tile radius, avoiding NPCs with the specified death animation.
    Hover over the NPC, check interaction options to decide left or right click.
    
    Args:
        npc_name (str): Name of the NPC to attack.
        tile_radius (int): Maximum distance in tiles to consider NPCs (default: 10).
        death_animation (int, optional): Animation ID to avoid (e.g., death animation). Defaults to None.
    
    Returns:
        dict: The selected NPC data if attack is successful, None otherwise.
    """
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player data.")
        return None

    p_loc = player_data['data']['location']
    p_x = p_loc['x']
    p_y = p_loc['y']

    npc_data = npc(name=npc_name, tile=True, middle_point=True)
    print(npc_data)
    if not npc_data or 'data' not in npc_data or not npc_data['data']:
        print(f"No {npc_name} found.")
        return None

    closest = None
    min_dist = float('inf')
    for n in npc_data['data']:
        if 'tile' not in n or 'middle_point' not in n:
            continue
        # Skip NPCs with the specified death animation
        if death_animation is not None and n.get('animation') == death_animation:
            continue
        n_tile = n['tile']
        dx = abs(n_tile['x'] - p_x)
        dy = abs(n_tile['y'] - p_y)
        dist = math.sqrt(dx**2 + dy**2)
        if dist <= tile_radius and dist < min_dist:
            min_dist = dist
            closest = n

    if not closest:
        print(f"No {npc_name} within {tile_radius} tiles or all are in death animation.")
        return None

    mid = closest['middle_point']
    screen_x = rl_x + mid['x']
    screen_y = rl_y + mid['y']

    # Hover over the NPC to load interaction options
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.05, 0.1))

    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available.")
        return None

    npc_names_list = [npc_name.lower()]

    first_option = options[0]
    if first_option['option'] == 'Attack' and any(name in first_option['target'].lower() for name in npc_names_list):
        move(screen_x, screen_y, fast=True, button='left', sleep=True)
        return closest

    found_attack_option = False
    x_r, y_r = 0, 0
    for option in options:
        if option['option'] == 'Attack' and any(name in option['target'].lower() for name in npc_names_list):
            x_r = option['middle_point']['x'] + rl_x
            y_r = option['middle_point']['y'] + rl_y
            found_attack_option = True
            break

    if found_attack_option:
        move(screen_x, screen_y, fast=True, button='right', sleep=True)
        time.sleep(random.uniform(0.05, 0.1))
        move(x_r, y_r, fast=True, button='left', sleep=True)
        return closest

    print(f"No 'Attack' option found for {npc_name}.")
    return None

# Example usage with death animation for Moss Giant (4658 from npc_data)
attack('moss giant', death_animation=4659)
