import math
import random
import time
import re
from typing import Optional, Dict, Any
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, interact_options, tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
from modules.utils.select_menu_option import select_menu_option
from modules.core.window_utils import runelite_window
from modules.core.mouse_control import move, left_click, right_click

def is_player_idle():
    """
    Check if the player is idle (not moving) based on animation and tile stability.
    
    Returns:
    - True if player's tile hasn't changed in the last tick and animation is idle, False otherwise.
    """
    pl_data = player(location=True, animation=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data'] or 'animation' not in pl_data['data']:
        print("Failed to fetch player location or animation")
        return False
    
    initial_loc = pl_data['data']['location']
    initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
    animation = pl_data['data']['animation']
    
    wait_for_tick(ticks=1)
    
    pl_data = player(location=True, animation=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location after tick")
        return False
    
    current_loc = pl_data['data']['location']
    current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
    
    is_idle = current_tile == initial_tile and pl_data['data']['animation'] in [0, -1]
    print(f"Player idle check: Tile unchanged: {current_tile == initial_tile}, Animation: {pl_data['data']['animation']}, Idle: {is_idle}")
    return is_idle

def check_if_in_tile(x, y, plane=0, click=False, force_right_click=False, action="Walk here", tile_radius=1):
    """
    Check if the player is standing on the specific tile.
    
    Parameters:
    - x: Tile x-coordinate.
    - y: Tile y-coordinate.
    - plane: Tile plane (defaults to 0).
    - click: If True, click the tile on minimap if visible and walkable, if not on tile.
    - force_right_click: If True, forces right-click and menu selection.
    - action: The action to perform on the tile (defaults to "Walk here").
    - tile_radius: Radius for random tile selection (defaults to 1 for exact tile).
    
    Returns:
    - True if on tile (or successfully moved to it), False otherwise.
    
    From different views:
    - Functionality: Compares player tile to target; clicks exact visible walkable tile.
    - Reliability: Waits for idle state before retrying, uses 5 retries and walkable checks.
    - Performance: Checks if target tile is visible on minimap, no bounding box needed.
    - Bigger picture: Ensures exact positioning in RuneScape for tasks like precise interactions or safe spots.
    """
    target_tile = (x, y, plane)
    print(f"Target tile: {target_tile}")

    # Get initial player position
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location")
        return False
    loc = pl_data['data']['location']
    px, py, pplane = loc['x'], loc['y'], loc['plane']
    player_tile = (px, py, pplane)
    print(f"Initial player location: {player_tile}")

    # Check if player is on the target tile
    if player_tile == target_tile:
        print("Player is on the target tile")
        return True

    if not click:
        print("Player not on tile, click=False, returning False")
        return False

    # Attempt to move to tile, max 5 tries
    max_tries = 5
    for attempt in range(max_tries):
        print(f"Attempt {attempt + 1}/{max_tries} to move to tile")
        # Get current player position
        pl_data = player(location=True, animation=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location during attempt")
            return False
        loc = pl_data['data']['location']
        px, py, pplane = loc['x'], loc['y'], loc['plane']
        print(f"Current player position: ({px}, {py}, {pplane})")

        # Check if player is already on the tile before clicking
        if (px, py, pplane) == target_tile:
            print("Player is on the target tile after position check")
            return True

        # Click the tile using the new function
        if not click_tile(x, y, plane, action, tile_radius, force_right_click):
            print("Failed to click tile")
            return False

        # Wait for tile change, short timeout
        print("Waiting for tile change")
        if not wait_for_tile_change(timeout_ticks=1):  # ~0.6 seconds
            print("Tile did not change after click")
            print("Waiting for player to stop moving before retry")
            while not is_player_idle():
                print("Player still moving, waiting another tick")
            continue

        # Check if now on tile
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location after move")
            continue
        loc = pl_data['data']['location']
        px, py, pplane = loc['x'], loc['y'], loc['plane']
        new_tile = (px, py, pplane)
        print(f"New player location after move: {new_tile}")
        if new_tile == target_tile:
            print("Successfully moved to target tile")
            return True

        # Wait until player is idle before retrying
        print("Player moved but not on tile, waiting for idle before retry")
        while not is_player_idle():
            print("Player still moving, waiting another tick")

    print(f"Failed to move to tile after {max_tries} attempts")
    return False

def click_tile(x: int, y: int, plane: int = 0, action: str = "Walk here", tile_radius: int = 1, right_click: bool = False) -> bool:
    """
    Clicks on the specified tile (or nearby based on radius) with the given action using select_menu_option.
    
    Parameters:
    - x: Tile x-coordinate.
    - y: Tile y-coordinate.
    - plane: Tile plane (defaults to 0).
    - action: The action to perform (defaults to "Walk here").
    - tile_radius: Radius for selecting a random adjacent tile (defaults to 1 for exact).
    - right_click: If True, forces right-click and menu selection even for default actions.
    
    Returns:
    - True if successfully clicked, False otherwise.
    """
    target_base = (x, y, plane)
    print(f"Target base tile: {target_base}")

    # Determine target tile with radius
    if tile_radius == 1:
        target_x, target_y = x, y
    else:
        offset = tile_radius - 1
        choices = [(offset, 0), (-offset, 0), (0, offset), (0, -offset), (0, 0)]
        dx, dy = random.choice(choices)
        target_x, target_y = x + dx, y + dy
    print(f"Selected target tile: ({target_x}, {target_y})")

    # Get player plane to check
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location")
        return False
    loc = pl_data['data']['location']
    px, py, pplane = loc['x'], loc['y'], loc['plane']
    if pplane != plane:
        print("Plane mismatch")
        return False

    # Check if already on the selected target tile
    if (target_x, target_y) == (px, py):
        print("Already on selected target tile, no click needed")
        return True

    # Check walkable
    walkable_data = walkable_tile(target_x, target_y, tile_radius=100, middle_point=False).get('data', [])
    is_walkable = any(t['x'] == target_x and t['y'] == target_y and t['plane'] == plane for t in walkable_data)
    if not is_walkable:
        print(f"Target tile ({target_x}, {target_y}) is not walkable")
        return False
    print(f"Target tile ({target_x}, {target_y}) is walkable, distance: {math.hypot(target_x - px, target_y - py):.2f} tiles")

    # Get tile data for main screen position
    tile_data = tile(tile_x=target_x, tile_y=target_y, tile_radius=100, middle_point=True).get('data', [])
    tile_entry = next((t for t in tile_data if t['x'] == target_x and t['y'] == target_y and t['plane'] == plane), None)
    if not tile_entry:
        print(f"Target tile ({target_x}, {target_y}) not visible on main screen")
        return False

    if 'middle_point' not in tile_entry:
        print("Tile entry does not have middle_point")
        return False
    canvas_x = tile_entry['middle_point']['x']
    canvas_y = tile_entry['middle_point']['y']

    # Get screen coordinates
    rl_x, rl_y = runelite_window(0, 0)
    screen_x = rl_x + canvas_x
    screen_y = rl_y + canvas_y

    # Hover to load options
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.05, 0.1))

    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available.")
        return False

    action_normalized = ' '.join(action.lower().split())

    # Find matched option
    matched_option = None
    for option in options:
        option_target_clean = re.sub(r'<[^>]+>', '', option['target']).lower()
        option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
        if option['option'].lower() == action_normalized or option_combined == action_normalized:
            matched_option = option
            break

    if not matched_option:
        print(f"No '{action}' option found. Available options: {[f'{opt['option']} {re.sub(r'<[^>]+>', '', opt['target'])}' for opt in options]}")
        return False

    # Check if first option matches
    first_option = options[0]
    first_target_clean = re.sub(r'<[^>]+>', '', first_option['target']).lower()
    first_combined = f"{first_option['option'].lower()} {first_target_clean}".strip()
    is_first_matching = (first_option['option'].lower() == action_normalized or first_combined == action_normalized)

    if is_first_matching and not right_click:
        # Left-click for default
        move(screen_x, screen_y, fast=True, sleep=True, button='left')
        print(f"Left-clicked for action '{action}'")
    else:
        # Right-click and select from menu
        move(screen_x, screen_y, fast=True, sleep=True, button='right')
        time.sleep(random.uniform(0.05, 0.1))
        action_x = rl_x + matched_option['middle_point']['x']
        action_y = rl_y + matched_option['middle_point']['y']
        move(action_x, action_y, fast=True, sleep=True, button='left')
        print(f"Right-clicked and selected action '{action}'")

    return True


# click_tile(1629, 3939, plane=0, action="Walk here", tile_radius=2, right_click=False)

# Example usage:
# check_if_in_tile(2196, 3811, 0, click=True, right_click=True)
# or check_if_in_tile(2196, 3811, click=True)  # plane defaults to 0