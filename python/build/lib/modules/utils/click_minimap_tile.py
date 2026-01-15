import random
import pyautogui
import time
from modules.core.mouse_control import move, scroll
from modules.core.plugin_client import minimap_tile_point, player
from modules.core.window_utils import runelite_window

# zoom = 2.0 is minimum, 4.0 is normal, 10.0 is maximum

def click_minimap_tile(target_x, target_y, rand_x=0, rand_y=0, right_click=False, target_zoom: float = None):
    
    rl_x, rl_y = runelite_window(0, 0)
    """Click a random minimap tile around the target coordinates, optionally setting zoom first."""
    if target_zoom is not None:
        # Get player position to find minimap center
        player_data = player(location=True)
        if not player_data or 'data' not in player_data:
            print("Failed to get player location.")
            return False
        loc = player_data['data']['location']
        player_x = loc['x']
        player_y = loc['y']

        # Get minimap center and current zoom
        center_data = minimap_tile_point(player_x, player_y)
        if not center_data or 'data' not in center_data:
            print("Failed to get minimap center.")
            return False
        data = center_data['data']
        if 'error' in data:
            print(f"Error getting minimap center: {data['error']}")
            return False
        current_zoom = data.get('zoom', 4.0)  # Default to 4.0 if not present
        center_x = data['x'] + rl_x
        center_y = data['y'] + rl_y

        # Calculate steps
        step = 0.25
        diff = target_zoom - current_zoom
        if abs(diff) < 0.01:  # Already at target zoom (accounting for float precision)
            print(f"Current zoom {current_zoom} already matches target {target_zoom}. Skipping adjustment.")
        else:
            steps = int(round(diff / step))  # Round to nearest increment
            direction = 1 if diff > 0 else -1  # Scroll up (1) to increase zoom, down (-1) to decrease
            # Hover over center
            move(center_x, center_y, button=None, fast=True, sleep=False)
            time.sleep(0.01)

            # Simulate scrolls
            for _ in range(abs(steps)):
                scroll(direction, sleep=random.uniform(0.015, 0.04))

            # Optional: Verify final zoom
            center_data = minimap_tile_point(player_x, player_y)
            if center_data and 'data' in center_data and 'zoom' in center_data['data']:
                final_zoom = center_data['data']['zoom']
                print(f"Set zoom to {final_zoom} (target: {target_zoom})")

    # Proceed with clicking
    dx = random.randint(-rand_x, rand_x)
    dy = random.randint(-rand_y, rand_y)
    target_tile_x = target_x + dx
    target_tile_y = target_y + dy
    print(f"Attempting to click minimap tile ({target_tile_x}, {target_tile_y})")

    minimap_data = minimap_tile_point(target_tile_x, target_tile_y)
    if not minimap_data or 'data' not in minimap_data:
        print("No minimap tile data available or error occurred.")
        return False

    data = minimap_data['data']
    if 'error' in data:
        print(f"Target tile ({target_tile_x}, {target_tile_y}) not visible on minimap: {data['error']}")
        return False

    click_x = data['x'] + rl_x
    click_y = data['y'] + rl_y

    if right_click:
        print(f"Found minimap point for tile ({target_tile_x}, {target_tile_y}) at screen coords: ({click_x}, {click_y + 1}). Right-clicking.")
        move(click_x, click_y + 1, button='right', fast=True, sleep=True)
        minimap_data = minimap_tile_point(target_tile_x, target_tile_y)
        if not minimap_data or 'data' not in minimap_data:
            print("No minimap tile data available after right-click.")
            return False

        data = minimap_data['data']
        if 'error' in data:
            print(f"Target tile ({target_tile_x}, {target_tile_y}) not visible on minimap after right-click: {data['error']}")
            return False

        click_x = data['x'] + rl_x
        click_y = data['y'] + rl_y 
        print(f"Found minimap point for tile ({target_tile_x}, {target_tile_y}) at screen coords: ({click_x}, {click_y + 1}). Left-clicking.")
        move(click_x + 1, click_y + 1, button='left', fast=True, sleep=True)
        return True
    else:
        print(f"Found minimap point for tile ({target_tile_x}, {target_tile_y}) at screen coords: ({click_x}, {click_y + 1}). Clicking.")
        move(click_x + 1 , click_y + 1, button='left', fast=True, sleep=True)
        return True

# click_minimap_tile(2630, 3123, 0, 0, target_zoom=2)