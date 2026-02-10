import math
import random
import time
import re
from typing import Optional, Dict, Any
from modules.core.plugin_client import player, walkable_tile, interact_options, tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
from modules.utils.select_menu_option import select_menu_option
from modules.core.window_utils import runelite_window
from modules.core.mouse_control import move, left_click, right_click
from modules.utils.click_minimap_tile import click_minimap_tile

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
            # print("Tile did not change after click")
            # print("Waiting for player to stop moving before retry")
            # while not is_player_idle():
            #     print("Player still moving, waiting another tick")
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


def click_tile(x: int, y: int, plane: int = 0, action: str = "Walk here", tile_radius: int = 20, right_click: bool = False) -> bool:
    """
    Clicks on the specified tile using main-screen click if possible.
    - tile_radius now strictly controls the search radius around the target for visible/on-screen walkable tiles.
    - Always prefers the exact target tile if visible.
    - If exact tile is off-screen, picks the closest visible walkable tile to the target within the exact radius provided.
    - If no visible tile found within radius -> falls back to click_minimap_tile.
    """
    target_base = (x, y, plane)
    print(f"Target base tile: {target_base}, search radius: {tile_radius}")

    # Get player position
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location")
        return False
    loc = pl_data['data']['location']
    px, py, pplane = loc['x'], loc['y'], loc['plane']
    if pplane != plane:
        print("Plane mismatch")
        return False

    dist_to_target = math.hypot(x - px, y - py)
    print(f"Distance to target: {dist_to_target:.2f} tiles")

    if dist_to_target < 1:
        print("Already on target tile")
        return True

    # Use exactly the provided tile_radius for both API calls (faster, no oversized search)
    tile_data = tile(tile_x=x, tile_y=y, tile_radius=tile_radius, middle_point=True).get('data', [])
    walkable_data = walkable_tile(x, y, tile_radius=tile_radius, middle_point=False).get('data', [])

    # Candidates: visible (has middle_point) + walkable + within exact tile_radius of target
    candidates = []
    for t in tile_data:
        if 'middle_point' not in t:
            continue
        if not any(w['x'] == t['x'] and w['y'] == t['y'] and w['plane'] == plane for w in walkable_data):
            continue
        dist_from_target = math.hypot(t['x'] - x, t['y'] - y)
        if dist_from_target > tile_radius:
            continue
        candidates.append(t)

    if not candidates:
        print(f"No visible walkable tile within exact radius {tile_radius} -> falling back to minimap click")
        # Minimap fallback using your helper
        success = click_minimap_tile(
            x,
            y,
            rand_x=3,
            rand_y=3,
            target_zoom=2.0
        )
        if success:
            print("Minimap click successful")
            return True
        print("Minimap click failed")
        return False

    # Prefer exact tile first, then closest to target
    candidates.sort(key=lambda t: (0 if (t['x'], t['y']) == (x, y) else 1, math.hypot(t['x'] - x, t['y'] - y)))

    selected_tile = candidates[0]
    print(f"Selected tile: ({selected_tile['x']}, {selected_tile['y']}), distance from target: {math.hypot(selected_tile['x'] - x, selected_tile['y'] - y):.2f}")

    canvas_x = selected_tile['middle_point']['x']
    canvas_y = selected_tile['middle_point']['y']

    rl_x, rl_y = runelite_window(0, 0)
    screen_x = rl_x + canvas_x
    screen_y = rl_y + canvas_y

    # Hover to load options
    print(f"Hovering to x: {screen_x}, y: {screen_y}")
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.05, 0.12))

    options = interact_options().get('data', [])
    if not options:
        print("No interaction options after hover")
        return False

    action_normalized = ' '.join(action.lower().split())

    matched_option = None
    for opt in options:
        opt_target_clean = re.sub(r'<[^>]+>', '', opt['target']).lower()
        opt_combined = f"{opt['option'].lower()} {opt_target_clean}".strip()
        if opt['option'].lower() == action_normalized or opt_combined == action_normalized:
            matched_option = opt
            break

    if not matched_option:
        print(f"No '{action}' option found. Available: {[f'{o['option']} {re.sub(r'<[^>]+>', '', o['target'])}' for o in options]}")
        return False

    first_opt = options[0]
    first_target_clean = re.sub(r'<[^>]+>', '', first_opt['target']).lower()
    first_combined = f"{first_opt['option'].lower()} {first_target_clean}".strip()
    is_default = (first_opt['option'].lower() == action_normalized or first_combined == action_normalized)

    if is_default and not right_click:
        move(screen_x, screen_y, button='left', fast=True, sleep=True)
        print(f"Left-clicked tile ({selected_tile['x']}, {selected_tile['y']}) for default '{action}'")
    else:
        move(screen_x, screen_y, button='right', fast=True, sleep=True)
        time.sleep(random.uniform(0.05, 0.1))
        opt_x = rl_x + matched_option['middle_point']['x']
        opt_y = rl_y + matched_option['middle_point']['y']
        move(opt_x, opt_y, button='left', fast=True, sleep=True)
        print(f"Right-clicked and selected '{action}' on tile ({selected_tile['x']}, {selected_tile['y']})")

    return True

# click_tile(1629, 3939, plane=0, action="Walk here", tile_radius=2, right_click=False)

# Example usage:
# check_if_in_tile(2196, 3811, 0, click=True, right_click=True)
# or check_if_in_tile(2196, 3811, click=True)  # plane defaults to 0