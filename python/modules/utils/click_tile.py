from modules.core.plugin_client import minimap_tile_point
from modules.core.mouse_control import move, left_click
from modules.core.window_utils import runelite_window
from modules.utils.select_menu_option import select_menu_option  # Your provided function
import random
import time

def click_tile(tile_x: int, tile_y: int, plane: int = 0, action: str = "Walk here", 
               tile_radius: int = 0, right_click: bool = False, rand_x: int = 5, rand_y: int = 5) -> bool:
    """
    Clicks a world tile (or random tile within radius) by finding its point on the minimap.
    - If tile_radius > 0: Picks a random tile within manhattan distance <= radius.
    - Uses minimap_tile_point() to get canvas coordinates.
    - Adds randomization around the minimap point.
    - Supports:
        - Left-click (default for "Walk here").
        - Right-click only.
        - Right-click + select action from menu (using your select_menu_option).
    - Returns True if click performed successfully, False otherwise.
    """
    # Random tile within radius if specified
    if tile_radius > 0:
        while True:
            offset_x = random.randint(-tile_radius, tile_radius)
            offset_y = random.randint(-tile_radius, tile_radius)
            if abs(offset_x) + abs(offset_y) <= tile_radius:
                break
        target_x = tile_x + offset_x
        target_y = tile_y + offset_y
    else:
        target_x = tile_x
        target_y = tile_y

    point_data = minimap_tile_point(target_x, target_y, plane)
    if not point_data or 'data' not in point_data:
        print(f"Failed to get minimap point for tile ({target_x}, {target_y}, plane={plane})")
        return False

    data = point_data['data']
    canvas_x = data['x']
    canvas_y = data['y']

    # Random offset on minimap point
    offset_x = random.randint(-rand_x, rand_x)
    offset_y = random.randint(-rand_y, rand_y)
    click_canvas_x = canvas_x + offset_x
    click_canvas_y = canvas_y + offset_y

    # Convert to absolute screen coords
    abs_x, abs_y = runelite_window(click_canvas_x, click_canvas_y)

    if action and right_click:
        # Right-click and select action using your function
        move(abs_x, abs_y, fast=True, sleep=True, button='right')
        time.sleep(random.uniform(0.05, 0.1))
        result = select_menu_option(click_canvas_x, click_canvas_y, action, hover_only=False)
        return result is not None
    elif right_click:
        # Simple right-click
        move(abs_x, abs_y, fast=True, sleep=True, button='right')
        return True
    else:
        # Left-click (default Walk here)
        move(abs_x, abs_y, fast=True, sleep=True, button='left')
        return True