# slayer_master_edgeville.py
# A script for navigating to the Slayer Master Vannaka in Edgeville Dungeon in Old School RuneScape via RuneLite plugin.
from modules.widgets.widget import get_widget, click_widget
from modules.player_data.click_equipment import click_equipment_item
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.object_data.object import click_object, check_object, get_closest_object
from modules.npc_data.click_npc import get_player_position, click_npc
from modules.core.window_utils import focus_runelite_window
from modules.utils.wait_for_tick import wait_for_tick
from modules.utils.camera import camera
from modules.utils.logout import logout
import time
import random

# Corrected widget ID for equipment tab based on RuneLite API
EQUIPMENT_TAB_WIDGET_ID = '35913796'
EQUIPMENT_TAB_SELECTED_SPRITE_ID = 1030

def check_and_open_equipment_tab() -> bool:
    """
    Checks if the equipment tab is open by looking at the widget's sprite ID.
    If not open (sprite ID != 1030), clicks the widget to open it.
    Returns True if open or opened successfully, False otherwise.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Get the equipment tab widget
    tab_widget = get_widget(EQUIPMENT_TAB_WIDGET_ID)
    if not tab_widget:
        print("Equipment tab widget not found.")
        return False

    # Print the current sprite ID for debugging
    current_sprite_id = tab_widget.get('spriteId', -1)
    print(f"Current sprite ID for equipment tab: {current_sprite_id}")

    # Check if it's already open
    if current_sprite_id == EQUIPMENT_TAB_SELECTED_SPRITE_ID:
        print("Equipment tab is already open.")
        return True

    # If not selected, click to open with random offsets
    success = click_widget(EQUIPMENT_TAB_WIDGET_ID, rand_x=5, rand_y=5)
    if success:
        print("Opened equipment tab successfully.")
        time.sleep(0.5)  # Short delay to allow tab to open
        return True
    else:
        print("Failed to click equipment tab widget.")
        return False

def teleport_to_edgeville() -> bool:
    """
    Hovers over an equipped Amulet of Glory (any charge level),
    selects the 'Edgeville' teleport option, and waits for the tile to change.
    Returns True if successful, False otherwise.
    """
    # First, ensure equipment tab is open
    if not check_and_open_equipment_tab():
        return False

    # Click (right-click and select) the amulet with 'Edgeville' option
    # Partial name match will catch 'Amulet of glory(n)'
    success = click_equipment_item("Amulet of glory", action="Edgeville")
    if not success:
        print("Failed to select Edgeville teleport on Amulet of Glory.")
        return False

    print("Selected Edgeville teleport.")

    # Wait for tile change (teleport completion)
    tile_changed = wait_for_tile_change(timeout_ticks=20)
    if tile_changed:
        print("Teleport successful: Tile has changed.")
        # Adjust camera after teleport
        camera_adjusted = camera(pitch=319, yaw=1927, zoom=307)
        if camera_adjusted:
            print("Camera adjusted successfully after teleport.")
        else:
            print("Failed to adjust camera after teleport.")
            return False
        return True
    else:
        print("Timeout waiting for tile change after teleport.")
        return False

def wait_for_specific_tile(target_x: int, target_y: int, target_plane: int = 0, timeout: float = 30.0, check_interval: float = 0.5) -> bool:
    """
    Waits until the player's position matches the target tile.
    Polls every check_interval seconds until timeout.
    Returns True if reached within timeout, False otherwise.
    """
    start_time = time.time()
    while time.time() - start_time < timeout:
        current_pos = get_player_position()
        if current_pos == (target_x, target_y, target_plane):
            print(f"Reached target tile: ({target_x}, {target_y}, {target_plane})")
            return True
        time.sleep(check_interval)
    print(f"Timeout waiting for target tile: ({target_x}, {target_y}, {target_plane})")
    return False

def navigate_to_dungeon() -> bool:
    """
    Performs the navigation sequence:
    1. Click minimap tile (3094, 3470) with zoom 2.
    2. Wait until character stops moving.
    3. Click object 1579 with "Open".
    4. Wait until character stops moving.
    5. Click object 1581 with "Climb-down".
    6. Wait until on tile (3096, 9867, plane=0).
    Returns True if all steps successful, False otherwise.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Step 1: Click minimap tile
    clicked = click_minimap_tile(3094, 3470, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile.")
        return False
    print("Clicked minimap tile (3094, 3470).")

    # Step 2: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after minimap click.")
        return False

    # Step 3: Try click object with "Open"
    closest_open = get_closest_object('1579', 'Open')
    if closest_open:
        wait_for_tick(ticks=random.randint(3, 5))
        opened = click_object('1579', 'Open')
        if not opened:
            print("Failed to click object 1579 with 'Open' after finding.")
            return False
        print("Clicked object 1579 with 'Open'.")
    else:
        opened = False

    if not opened:
        # Assume already open, try "Climb-down" directly
        closest_climb = get_closest_object('1581', 'Climb-down')
        if closest_climb:
            wait_for_tick(ticks=random.randint(3, 5))
            climbed = click_object('1581', 'Climb-down')
            if not climbed:
                print("Failed to click object 1581 with 'Climb-down' after finding.")
                return False
            print("Clicked object 1581 with 'Climb-down'.")
        else:
            print("Object 1581 with 'Climb-down' not found.")
            return False
        # Wait until stopped moving after climb-down
        stopped = wait_till_character_stopped_moving()
        if not stopped:
            print("Timeout waiting for character to stop moving after climb-down.")
            return False
    else:
        # Opened successfully, wait until stopped moving after open
        stopped = wait_till_character_stopped_moving()
        if not stopped:
            print("Timeout waiting for character to stop moving after opening.")
            return False
        # Now click "Climb-down"
        closest_climb = get_closest_object('1581', 'Climb-down')
        if closest_climb:
            wait_for_tick(ticks=random.randint(3, 5))
            climbed = click_object('1581', 'Climb-down')
            if not climbed:
                print("Failed to click object 1581 with 'Climb-down' after finding.")
                return False
            print("Clicked object 1581 with 'Climb-down' after opening.")
        else:
            print("Object 1581 with 'Climb-down' not found after opening.")
            return False
        # Wait until stopped moving after climb-down
        stopped = wait_till_character_stopped_moving()
        if not stopped:
            print("Timeout waiting for character to stop moving after climb-down.")
            return False

    # Step 6: Wait until on specific tile
    reached = wait_for_specific_tile(3096, 9867, 0)
    if not reached:
        return False

    print("Navigation to dungeon entrance completed successfully.")
    return True

def navigate_dungeon() -> bool:
    """
    Navigates within the dungeon after reaching (3096, 9867):
    1. Click minimap tile (3095, 9902).
    2. Wait until character stops moving.
    3. Check if object 1569 with "Open" exists; if so, click it with "Open".
    4. Click minimap tile (3129, 9911).
    5. Wait until character stops moving.
    6. Click minimap tile (3145, 9913).
    7. Wait until character stops moving.
    8. Click NPC 'Vannaka' with 'Assignment'.
    9. Wait until character stops moving.
    Returns True if successful, False otherwise.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Step 1: Click minimap tile (3095, 9902)
    clicked = click_minimap_tile(3095, 9902, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3095, 9902).")
        return False
    print("Clicked minimap tile (3095, 9902).")

    # Step 2: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after first dungeon minimap click.")
        return False

    # Step 3: Check and click object 1569 with "Open" if exists
    if check_object('1569', 'Open'):
        opened = click_object('1569', 'Open')
        if not opened:
            print("Failed to click object 1569 with 'Open'.")
            return False
        print("Clicked object 1569 with 'Open'.")
        # Wait until stopped moving after opening
        stopped = wait_till_character_stopped_moving()
        if not stopped:
            print("Timeout waiting for character to stop moving after opening object 1569.")
            return False
    else:
        print("Object 1569 with 'Open' not found; proceeding.")

    # Step 4: Click minimap tile (3129, 9911)
    clicked = click_minimap_tile(3129, 9911, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3129, 9911).")
        return False
    print("Clicked minimap tile (3129, 9911).")

    # Step 5: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after second dungeon minimap click.")
        return False

    # Step 6: Click minimap tile (3145, 9913)
    clicked = click_minimap_tile(3145, 9913, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3145, 9913).")
        return False
    print("Clicked minimap tile (3145, 9913).")

    # Step 7: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after third dungeon minimap click.")
        return False

    wait_for_tick(ticks=random.randint(3, 15))
    

    # Step 8: Click NPC 'Vannaka' with 'Assignment'
    npc_clicked = click_npc('Vannaka', 'Assignment')
    if not npc_clicked:
        print("Failed to click NPC Vannaka with 'Assignment'.")
        return False
    print("Task assigned.")
    wait_for_tick(ticks=random.randint(3, 50))
    logout()
    return True

def full_navigation() -> bool:
    """
    Performs the full sequence: Teleport to Edgeville, navigate to dungeon entrance,
    then navigate within the dungeon.
    Returns True if all successful, False otherwise.
    """
    if not teleport_to_edgeville():
        return False
    if not navigate_to_dungeon():
        return False
    if not navigate_dungeon():
        return False
    print("Full navigation sequence completed.")
    return True

# Example usage: Run the full navigation
if __name__ == "__main__":
    full_navigation()