import math
import random
from modules.core.plugin_client import player, minimap_tiles, walkable_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick

def point_in_polygon(x, y, vertices):
    """
    Check if point (x, y) is inside or on the boundary of a polygon using ray-casting.
    
    Parameters:
    - x, y: Coordinates of the point to check.
    - vertices: List of (x, y) tuples defining the polygon.
    
    Returns:
    - True if point is inside or on the boundary, False otherwise.
    """
    n = len(vertices)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        # Check if point is on vertex or edge
        if (xi, yi) == (x, y) or (xj, yj) == (x, y):
            print(f"Point ({x}, {y}) is on vertex")
            return True
        if min(yi, yj) <= y <= max(yi, yj) and min(xi, xj) <= x <= max(xi, xj):
            if (xj - xi) * (y - yi) == (yj - yi) * (x - xi):
                print(f"Point ({x}, {y}) is on edge between ({xi}, {yi}) and ({xj}, {yj})")
                return True
        # Ray-casting for interior points
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
            print(f"Edge ({xi}, {yi}) to ({xj}, {yj}) crossed, inside: {inside}")
        j = i
    print(f"Point ({x}, {y}) inside polygon: {inside}")
    return inside

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

def check_if_in_area(area_tiles, click=False):
    """
    Check if the player is inside the polygon defined by area_tiles.
    
    Parameters:
    - area_tiles: List of tile strings like ["2201,3812,0", "2201,3808,0"] forming a closed polygon.
    - click: If True, click a random walkable tile inside the polygon visible on minimap if not in area.
    
    Returns:
    - True if in area (or successfully moved into it), False otherwise.
    
    From different views:
    - Functionality: Uses ray-casting for polygon check; clicks random walkable tile inside area.
    - Reliability: Waits for idle state before retrying, uses 5 retries and walkable checks.
    - Performance: Checks visible minimap tiles within polygon bounds, no distance limit.
    - Bigger picture: Ensures precise positioning in RuneScape for tasks like safe-spotting.
    """
    # Parse area tiles into set and list of vertices (x, y) for polygon
    area_set = set()
    vertices = []
    for tile_str in area_tiles:
        x, y, plane = map(int, tile_str.split(','))
        area_set.add((x, y, plane))
        vertices.append((x, y))
    
    if vertices[0] != vertices[-1]:
        vertices.append(vertices[0])
    # print(f"Polygon vertices: {vertices}")

    # Get initial player position
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location")
        return False
    loc = pl_data['data']['location']
    px, py, plane = loc['x'], loc['y'], loc['plane']
    player_tile = (px, py, plane)
    # print(f"Initial player location: {player_tile}")

    # Check if player is inside the polygon
    area_plane = int(area_tiles[0].split(',')[2])
    if plane == area_plane and point_in_polygon(px, py, vertices):
        # print("Player is inside the target area polygon")
        return True

    if not click:
        # print("Player not in area polygon, click=False, returning False")
        return False

    # Attempt to move into area, max 5 tries
    max_tries = 5
    for attempt in range(max_tries):
        # print(f"Attempt {attempt + 1}/{max_tries} to move into area")
        # Get current player position
        pl_data = player(location=True, animation=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location during attempt")
            return False
        loc = pl_data['data']['location']
        px, py, plane = loc['x'], loc['y'], loc['plane']
        # print(f"Current player position: ({px}, {py}, {plane})")

        # Check if player is already in the polygon before clicking
        if plane == area_plane and point_in_polygon(px, py, vertices):
            # print("Player is inside the target area polygon after position check")
            return True

        # Get visible minimap tiles
        mm_data = minimap_tiles().get('data', [])
        if not mm_data:
            print("No minimap tiles data available")
            return False

        # Find bounding box of polygon
        x_coords, y_coords = zip(*vertices)
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)

        # Generate all possible tiles in bounding box
        possible_tiles = []
        for x in range(min_x, max_x + 1):
            for y in range(min_y, max_y + 1):
                if point_in_polygon(x, y, vertices):
                    possible_tiles.append((x, y))

        # Filter for walkable tiles visible on minimap
        visible_in_area = []
        for x, y in possible_tiles:
            for entry in mm_data:
                if entry['tileX'] == x and entry['tileY'] == y:
                    dist = math.hypot(x - px, y - py)
                    walkable_data = walkable_tile(x, y, tile_radius=20, middle_point=False)
                    if walkable_data and walkable_data.get('data', []):
                        visible_in_area.append((dist, x, y))
                        # print(f"Found walkable tile ({x}, {y}, {plane}) in area, distance: {dist:.2f} tiles")

        if not visible_in_area:
            # print("No walkable tiles inside polygon visible on minimap")
            return False

        # Pick a random walkable tile
        _, ctx, cty = random.choice(visible_in_area)
        # print(f"Selected random walkable tile ({ctx}, {cty}, {plane}) inside polygon")

        # Click the exact tile
        if not click_minimap_tile(ctx, cty, rand_x=0, rand_y=0):
            print("Failed to click minimap tile")
            return False

        # Wait for tile change, short timeout
        print("Waiting for tile change")
        if not wait_for_tile_change(timeout_ticks=1):  # ~0.6 seconds
            # print("Tile did not change after click")
            # print("Waiting for player to stop moving before retry")
            while not is_player_idle():
                # print("Player still moving, waiting another tick")
                continue
            continue

        # Check if now in area
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location after move")
            continue
        loc = pl_data['data']['location']
        px, py, plane = loc['x'], loc['y'], loc['plane']
        new_tile = (px, py, plane)
        # print(f"New player location after move: {new_tile}")
        if plane == area_plane and point_in_polygon(px, py, vertices):
            # print("Successfully moved into target area polygon")
            return True

        # Wait until player is idle before retrying
        # print("Player moved but not in area, waiting for idle before retry")
        while not is_player_idle():
            # print("Player still moving, waiting another tick")
            continue

    print(f"Failed to move into area after {max_tries} attempts")
    return False

# Example usage:
# area_tiles = [
# "2201,3812,0",
# "2201,3808,0",
# "2201,3806,0",
# "2203,3806,0",
# "2204,3807,0",
# "2205,3807,0",
# "2205,3812,0",
# "2201,3812,0",
# ]

# check_if_in_area(area_tiles, click=True)


# OR

# check_if_in_area(
# ["3214,3221,0",
# "3214,3211,0",
# "3227,3211,0",
# "3227,3226,0",
# "3217,3226,0",
# "3214,3221,0"])