import math
from modules.core.plugin_client import player, minimap_tiles, walkable_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick

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

def check_if_in_tile(x, y, plane=0, click=False, right_click=False):
    """
    Check if the player is standing on the specific tile.
    
    Parameters:
    - x: Tile x-coordinate.
    - y: Tile y-coordinate.
    - plane: Tile plane (defaults to 0).
    - click: If True, click the tile on minimap if visible and walkable, if not on tile.
    
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

        # Get visible minimap tiles
        mm_data = minimap_tiles().get('data', [])
        if not mm_data:
            print("No minimap tiles data available")
            return False

        # Check if target tile is visible and walkable
        is_visible = False
        for entry in mm_data:
            if entry['tileX'] == x and entry['tileY'] == y:
                is_visible = True
                break
        if not is_visible:
            print(f"Target tile ({x}, {y}, {plane}) not visible on minimap")
            return False

        walkable_data = walkable_tile(x, y, tile_radius=20, middle_point=False)
        if not walkable_data or not walkable_data.get('data', []):
            print(f"Target tile ({x}, {y}, {plane}) is not walkable")
            return False
        print(f"Target tile ({x}, {y}, {plane}) is walkable, distance: {math.hypot(x - px, y - py):.2f} tiles")

        # Click the exact tile
        if not click_minimap_tile(x, y, rand_x=0, rand_y=0, right_click=right_click):
            print("Failed to click minimap tile")
            return False

        # Wait for tile change, short timeout
        print("Waiting for tile change")
        if not wait_for_tile_change(timeout_ticks=1):  # ~0.6 seconds
            print("Tile did not change after click")
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

# Example usage:
# check_if_in_tile(2196, 3811, 0, click=True, right_click=True)
# or check_if_in_tile(2196, 3811, click=True)  # plane defaults to 0