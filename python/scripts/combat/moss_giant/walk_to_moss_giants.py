import time
import random
import keyboard 
from modules.core.plugin_client import inventory_random_clickpoint, player, interact_options, minimap_tiles, npc, game_object
from modules.core.mouse_control import move, scroll 
from modules.core.window_utils import runelite_window 
from modules.widgets.widget_data import get_all_widget_data 
from modules.utils.camera import camera 
from modules.utils.wait_for_tick import wait_for_tick 
from modules.utils.click_minimap_tile import click_minimap_tile

# Item name in inventory
TELEPORT_ITEM = "teleport to house"

# Widget IDs
MINIMAP_WIDGET_ID = 35913749
NORTH_BUTTON_WIDGET_ID = 35913751

# Get RuneLite window coordinates
rl_x, rl_y = runelite_window(0, 0)

def get_widget_random_point(widget_id):
    """Retrieve a random click point for a widget by its ID."""
    widgets = get_all_widget_data()
    if not widgets:
        print(f"No widget data found for ID {widget_id}")
        return None, None
    for widget in widgets:
        if widget.get('id') == widget_id:
            bounds = widget.get('bounds', {})
            if not bounds or 'x' not in bounds or 'width' not in bounds:
                print(f"Invalid bounds for widget ID {widget_id}: {bounds}")
                return None, None
            x = bounds['x'] + random.randint(0 + 10, bounds['width'] - 10)
            y = bounds['y'] + random.randint(0 + 10, bounds['height'] - 10)
            return x + rl_x, y + rl_y
    print(f"Widget ID {widget_id} not found")
    return None, None

# def click_minimap_tile(target_x, target_y, rand_x, rand_y, right_click=False):
    # """Click a random minimap tile around the target coordinates."""
    # dx = random.randint(-rand_x, rand_x)
    # dy = random.randint(-rand_y, rand_y)
    # target_tile_x = target_x + dx
    # target_tile_y = target_y + dy
    # print(f"Attempting to click minimap tile ({target_tile_x}, {target_tile_y})")

    # minimap_data = minimap_tiles().get('data', [])
    # if not minimap_data:
    #     print("No minimap tiles data available.")
    #     return False

    # for entry in minimap_data:
    #     if entry['tileX'] == target_tile_x and entry['tileY'] == target_tile_y:
    #         click_x = entry['clientX'] + rl_x
    #         click_y = entry['clientY'] + rl_y
    #         if right_click:
    #             move(click_x, click_y, button='right', fast=True, sleep=True)
    #             minimap_data = minimap_tiles().get('data', [])
    #             if not minimap_data:
    #                 print("No minimap tiles data available.")
    #                 return False

    #             for entry in minimap_data:
    #                 if entry['tileX'] == target_tile_x and entry['tileY'] == target_tile_y:
    #                     click_x = entry['clientX'] + rl_x
    #                     click_y = entry['clientY'] + rl_y
    #                     print(f"Found minimap point for tile ({target_tile_x}, {target_tile_y}) at screen coords: ({click_x}, {click_y}). Clicking.")
    #                     move(click_x, click_y, button='left', fast=True, sleep=True)
    #                     return True
    #         else:
    #             print(f"Found minimap point for tile ({target_tile_x}, {target_tile_y}) at screen coords: ({click_x}, {click_y}). Clicking.")
    #             move(click_x, click_y, button='left', fast=True, sleep=True)
    #             return True
            
    # print(f"Target tile ({target_tile_x}, {target_tile_y}) not visible on minimap.")
    # return False

def wait_for_y_threshold(threshold, timeout_sec=60):
    """Wait until the player's Y tile position is at or above the threshold."""
    start_time = time.time()
    while time.time() - start_time < timeout_sec:
        loc_data = player(location=True)
        if not loc_data or 'data' not in loc_data or 'location' not in loc_data['data']:
            time.sleep(0.1)
            continue
        current_y = loc_data['data']['location']['y']
        if current_y >= threshold:
            print(f"Reached Y threshold: {current_y} >= {threshold}")
            return True
        time.sleep(0.1)
    print(f"Timeout waiting for Y >= {threshold}")
    return False

def main():
    # Get initial player location
    initial_loc_data = player(location=True)
    if not initial_loc_data or 'data' not in initial_loc_data or 'location' not in initial_loc_data['data']:
        print("Failed to get initial player location.")
        return
    initial_loc = initial_loc_data['data']['location']
    print(f"Initial location: {initial_loc}")

    # Get teleport item position in inventory
    inv_data = inventory_random_clickpoint(TELEPORT_ITEM)
    if not inv_data or 'data' not in inv_data:
        print(f"Teleport item '{TELEPORT_ITEM}' not found in inventory.")
        return
    
    # Handle case where inv_data['data'] is a list
    items = inv_data['data']
    if not isinstance(items, list) or not items:
        print(f"No valid items found for '{TELEPORT_ITEM}' in inventory.")
        return
    
    # Select the first item (assuming one teleport item is sufficient)
    item = items[0]
    if 'random_clickpoint' not in item or 'x' not in item['random_clickpoint'] or 'y' not in item['random_clickpoint']:
        print(f"Invalid item data for '{TELEPORT_ITEM}': {item}")
        return
    item_x = item['random_clickpoint']['x'] + rl_x
    item_y = item['random_clickpoint']['y'] + rl_y
    print(f"Teleport item found at screen coords: ({item_x}, {item_y})")

    # Hover over the teleport item to check default action
    print(f"Hovering over teleport item at ({item_x}, {item_y})")
    move(item_x, item_y, fast=True, sleep=True)  # Move mouse without clicking
    time.sleep(random.uniform(0.1, 0.2))

    # Get interact options (potential menu)
    options_data = interact_options()
    if not options_data or 'data' not in options_data or not options_data['data']:
        print("No interact options found after hovering")
        return

    # Check the default (first) option
    first_option = options_data['data'][0]['option'].lower()
    if 'outside' in first_option:
        # Left-click directly
        print(f"Default action is '{first_option}', left-clicking at ({item_x}, {item_y})")
        move(item_x, item_y, button='left', fast=True)
    else:
        # Right-click and select 'Outside'
        print(f"First option is not 'outside' ({first_option}), right-clicking")
        move(item_x, item_y, button='right', fast=True)
        time.sleep(random.uniform(0.1, 0.3))
        options_data = interact_options()  # Now with open menu
        if not options_data or 'data' not in options_data:
            print("Failed to retrieve interaction options after right-click.")
            return

        # Debug: Print menu entries to inspect structure
        print(f"Menu entries after right-click: {options_data['data']}")

        # Find 'Outside' option
        outside_entry = next((entry for entry in options_data['data'] if entry.get('option', '').lower() == 'outside'), None)
        if outside_entry:
            # Use middle_point for menu coordinates, as per console output
            if 'middle_point' not in outside_entry or 'x' not in outside_entry['middle_point']:
                print(f"Invalid coordinate data for 'Outside' option: {outside_entry}")
                return
            option_x = outside_entry['middle_point']['x'] + rl_x
            option_y = outside_entry['middle_point']['y'] + rl_y
            print(f"'Outside' option found at screen coords: ({option_x}, {option_y}). Selecting it.")
            move(option_x, option_y, button='left', fast=True)
        else:
            print("'Outside' option not found in menu.")
            return

    # Wait until player has moved to a different tile
    print("Waiting for player to move to a different tile...")
    timeout = time.time() + 30  # 30-second timeout
    while time.time() < timeout:
        current_loc_data = player(location=True)
        if not current_loc_data or 'data' not in current_loc_data or 'location' not in current_loc_data['data']:
            print("Failed to get current player location.")
            time.sleep(0.1)
            continue
        current_loc = current_loc_data['data']['location']

        if (current_loc['x'] != initial_loc['x'] or
            current_loc['y'] != initial_loc['y'] or
            current_loc['plane'] != initial_loc['plane']):
            print(f"Player has moved to new location: {current_loc}")
            break
        time.sleep(0.1)
    else:
        print("Timeout waiting for player to move to a different tile.")
        return

    # Hover over minimap widget (ID 35913749)
    minimap_x, minimap_y = get_widget_random_point(MINIMAP_WIDGET_ID)
    if minimap_x is None or minimap_y is None:
        print(f"Failed to find minimap widget ID {MINIMAP_WIDGET_ID} for hovering.")
        return
    print(f"Hovering over minimap widget ID {MINIMAP_WIDGET_ID} at ({minimap_x}, {minimap_y})")
    move(minimap_x, minimap_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.1, 0.2))

    # Scroll down 15–20 times (adjusted from 25-30 as per script)
    scroll_count = random.randint(15, 20)
    print(f"Scrolling down {scroll_count} times")
    for _ in range(scroll_count):
        scroll(-1)
        time.sleep(random.uniform(0.02, 0.045))

    # Click north button widget (ID 35913751)
    north_x, north_y = get_widget_random_point(NORTH_BUTTON_WIDGET_ID)
    if north_x is None or north_y is None:
        print(f"Failed to find north button widget ID {NORTH_BUTTON_WIDGET_ID} for clicking.")
        return
    print(f"Clicking north button widget ID {NORTH_BUTTON_WIDGET_ID} at ({north_x}, {north_y})")
    move(north_x, north_y, button='left', fast=True)

    # Define the sequence of minimap clicks and Y thresholds
    path_steps = [
        (2663, 3645, 2, 1, 3643),
        (2657, 3657, 2, 2, 3654),
        (2650, 3665, 1, 2, 3663),
        (2642, 3673, 2, 1, 3672),
        (2630, 3678, 1, 1, 3677),
        (2621, 3687, 1, 1, 3686),
    ]

    success = True
    for step in path_steps:
        target_x, target_y, rand_x, rand_y, threshold = step
        if not click_minimap_tile(target_x, target_y, rand_x, rand_y):
            print(f"Failed to click minimap tile around ({target_x}, {target_y})")
            success = False
            break
        if not wait_for_y_threshold(threshold):
            print(f"Timeout waiting for Y >= {threshold}")
            success = False
            break

    if success:
        # Additional wait for Y >= 3685
        if not wait_for_y_threshold(3685):
            print("Timeout waiting for Y >= 3685")
            success = False
        else:
            # Set camera
            if not camera(pitch=293, yaw=0, zoom=265):
                print("Failed to adjust camera")
            else:
                # Find and interact with NPC ID 3855 (Lokar Searunner)
                for tick in range(3):
                    wait_for_tick()
                    print(tick)
                npc_data = npc("3855", middle_point=True)
                if not npc_data or 'data' not in npc_data or not npc_data['data']:
                    print("Failed to find Lokar Searunner")
                else:
                    entry = npc_data['data'][0]  # Assume closest/first one
                    if 'middle_point' not in entry:
                        print("No middle_point for NPC")
                    else:
                        mid_x = entry['middle_point']['x'] + rl_x
                        mid_y = entry['middle_point']['y'] + rl_y
                        # Hover over NPC
                        move(mid_x, mid_y, fast=True, sleep=True)
                        time.sleep(0.3)  # Wait for options to load
                        # Get interact options
                        options_data = interact_options()
                        if not options_data or 'data' not in options_data or not options_data['data']:
                            print("No interact options available")
                        else:
                            options = options_data['data']
                            # Check if the left-click option is "Pirate's Cove" (assuming first option is default/left-click)
                            if options and options[0].get('option') == "Pirate's Cove":
                                # Left click
                                move(mid_x, mid_y, button='left', fast=True)
                                print("Left-clicked on Pirate's Cove option")
                            else:
                                print("Left click option not 'Pirate's Cove'")
    if success:
        print("Reached final position and interacted successfully. Exiting script.")
        wait_for_widget_and_act()
        return True
    else:
        print("Script completed with errors.")
        return None

def check_widget_visible(widget_id):
    """
    Check if a widget is visible based on enabled status and valid bounds.
    
    Args:
        widget_id (int): The ID of the widget to check.
    
    Returns:
        bool: True if the widget is visible (enabled and has valid bounds), False otherwise.
    """
    widgets = get_all_widget_data()
    for widget in widgets:
        if widget.get('id') == widget_id:
            enabled = widget.get('enabled', False)
            bounds = widget.get('bounds', {})
            has_valid_bounds = bounds.get('width', 0) > 0 and bounds.get('height', 0) > 0
            return enabled and has_valid_bounds
    return False  # Widget not found or not visible

def wait_for_widget_and_act():
    """
    Wait for widget 10617398 to be visible, press space, wait for widget 14352385, press 1,
    fetch character tile, press space 3-5 times, and check for tile change up to 20 ticks.
    Exit as soon as a tile change is detected.
    """
    # Wait for widget 10617398 to be visible, max 20 ticks
    print("Waiting for widget 10617398 to become visible...")
    for _ in range(20):
        if check_widget_visible(10617398):
            keyboard.press_and_release('space')
            print("Pressed space for widget 10617398")
            time.sleep(random.uniform(0.07, 0.15))  # Short delay for stability
            break
        wait_for_tick()
    else:
        print("Timeout waiting for widget 10617398 to become visible")
        return False

    # Wait for widget 14352385 to be visible, max 10 ticks
    print("Waiting for widget 14352385 to become visible...")
    for _ in range(10):
        if check_widget_visible(14352385):
            keyboard.press_and_release('1')
            print("Pressed 1 for widget 14352385")
            time.sleep(random.uniform(0.07, 0.15))  # Short delay for stability
            break
        wait_for_tick()
    else:
        print("Timeout waiting for widget 14352385 to become visible")
        return False

    # Fetch current character tile
    player_data = player(location=True)
    current_tile = player_data.get('data', {}).get('location', {})
    if not current_tile:
        print("Failed to fetch character tile")
        return False
    print(f"Current tile: {current_tile}")

    # Press space 3-5 times with 0.07-0.15s interval
    wait_for_tick() 
    presses = random.randint(3, 5)
    print(f"Will press space {presses} times")
    for i in range(presses):
        keyboard.press_and_release('space')
        print(f"Pressed space {i+1}/{presses}")
        time.sleep(random.uniform(0.07, 0.15))  # Interval between presses

    # Check for tile change, max 20 ticks
    print("Checking for tile change...")
    initial_tile = current_tile.copy()
    for _ in range(20):
        player_data = player(location=True)
        new_tile = player_data.get('data', {}).get('location', {})
        if new_tile and new_tile != initial_tile:
            print(f"Tile changed to: {new_tile}")
            return True
        wait_for_tick()

    print("No tile change detected after 20 ticks")
    return False

def wait_for_tile_change(initial_tile, timeout_ticks=20):
    """
    Wait until the player's tile changes from the initial tile.
    Returns True if changed, False on timeout.
    """
    for _ in range(timeout_ticks):
        current_data = player(location=True)
        if not current_data or 'data' not in current_data or 'location' not in current_data['data']:
            wait_for_tick()
            continue
        current_tile = current_data['data']['location']
        if current_tile != initial_tile:
            print(f"Tile changed from {initial_tile} to {current_tile}")
            return True
        wait_for_tick()
    print("Timeout waiting for tile change")
    return False

def wait_for_specific_tile(target_x, target_y, timeout_ticks=40):
    """
    Wait until the player reaches the specific tile (x, y).
    Returns True if reached, False on timeout.
    """
    for _ in range(timeout_ticks):
        current_data = player(location=True)
        if not current_data or 'data' not in current_data or 'location' not in current_data['data']:
            wait_for_tick()
            continue
        current_tile = current_data['data']['location']
        if current_tile['x'] == target_x and current_tile['y'] == target_y:
            print(f"Reached target tile ({target_x}, {target_y})")
            return True
        wait_for_tick()
    print(f"Timeout waiting to reach tile ({target_x}, {target_y})")
    return False

def interact_with_object(object_id, action="Climb", tile=()):
    """
    Hover over the game object, check if left-click option is the desired action,
    if yes, left-click and return the middle point coordinates.
    Returns (mid_x, mid_y) if successful, None otherwise.
    """
    # Fetch object data (assuming game_object function similar to npc)
    obj_data = game_object(str(object_id), middle_point=True, tile=tile)
    if not obj_data or 'data' not in obj_data or not obj_data['data']:
        print(f"Failed to find game object {object_id}")
        return None
    entry = obj_data['data'][0]  # Assume first/closest one
    if 'middle_point' not in entry:
        print(f"No middle_point for object {object_id}")
        return None
    mid_x = entry['middle_point']['x'] + rl_x
    mid_y = entry['middle_point']['y'] + rl_y
    
    # Hover over object
    print(f"Hovering over object {object_id} at ({mid_x}, {mid_y})")
    move(mid_x, mid_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.1, 0.3))
    
    # Get interact options
    options_data = interact_options()
    if not options_data or 'data' not in options_data or not options_data['data']:
        print(f"No interact options for object {object_id}")
        return None
    
    # Check if left-click (first) option is the desired action
    first_option = options_data['data'][0].get('option', '').strip()
    if first_option == action:
        print(f"Left-click option is '{action}', clicking at ({mid_x}, {mid_y})")
        move(mid_x, mid_y, button='left', fast=True)
        return (mid_x, mid_y)
    else:
        print(f"Left-click option is '{first_option}', not '{action}' for object {object_id}")
        return None
    
def get_ladder_coordinates(tile_x=2212, tile_y=3809, plane=1):
    """
    Retrieve the screen coordinates (x, y) of the ladder at the specified tile and plane.

    Args:
        tile_x (int): X-coordinate of the ladder's tile (default: 2212).
        tile_y (int): Y-coordinate of the ladder's tile (default: 3809).
        plane (int): Plane of the ladder (default: 1).

    Returns:
        tuple: (screen_x, screen_y) if found, None otherwise.
    """
    # Fetch game object data for the specified tile
    obj_data = game_object(object="", tile=True, tile_radius=20, middle_point=True)
    if not obj_data or 'data' not in obj_data or not obj_data['data']:
        print(f"No game objects found at tile ({tile_x}, {tile_y})")
        return None

    # Filter for objects at the exact tile and plane
    for entry in obj_data['data']:
        tile = entry.get('tile', {})
        if (tile.get('x') == tile_x and 
            tile.get('y') == tile_y and 
            tile.get('plane') == plane):
            if 'middle_point' not in entry:
                print(f"No middle_point for object at tile ({tile_x}, {tile_y}, plane {plane})")
                return None
            mid_x = entry['middle_point']['x'] + rl_x
            mid_y = entry['middle_point']['y'] + rl_y
            print(f"Ladder found at tile ({tile_x}, {tile_y}, plane {plane}) with screen coords: ({mid_x}, {mid_y})")
            move(mid_x, mid_y, button='left', fast=True, sleep=True)
            return True

    
    print(f"No ladder found at tile ({tile_x}, {tile_y}, plane {plane})")
    return None

def walk_to_ladder():
    success = True
    
    # First object: 16960
    print("Processing object 16960...")
    # Get current tile before clicking
    initial_data = player(location=True)
    if not initial_data or 'data' not in initial_data or 'location' not in initial_data['data']:
        print("Failed to get initial player location")
        success = False
    else:
        initial_tile = initial_data['data']['location']
        print(f"Initial tile: {initial_tile}")
        
        if interact_with_object(16960):
            # Wait for tile change
            if not wait_for_tile_change(initial_tile):
                success = False
        else:
            success = False
    
    if not success:
        print("Failed processing object 16960")
        return
    
    for _ in range(3):
        wait_for_tick()

    # Second object: 16962
    print("Processing object 16962...")
    if get_ladder_coordinates():
        # Wait for specific tile (2211, 3809)
        if not wait_for_specific_tile(2211, 3809):
            success = False
    else:
        success = False
    
    if success:
        print("Successfully climbed both objects and reached target tile")
    else:
        print("Failed to complete the climb sequence")


# time.sleep(2)   
def walk_to_moss_giant():
    if main():
        for _ in range(6):
            wait_for_tick()
        if walk_to_ladder():
            print("Script completed successfully")
            return True
        else:
            print('walk to ladder failed')
    else:
        print("Main failed")

