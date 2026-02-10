# slayer_master_edgeville.py
# A script for navigating to the Slayer Master Vannaka in Edgeville Dungeon in Old School RuneScape via RuneLite plugin.
import keyboard
from modules.utils.automatic_scripting.small_functions import click_lowest_glory
from modules.widgets.widget import check_widget_text, click_widget_child, get_widget, click_widget
from modules.player_data.click_equipment import click_equipment_item
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.object_data.object import click_object, check_object, get_closest_object
from modules.npc_data.click_npc import get_player_position, click_npc
from modules.core.window_utils import focus_runelite_window
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.utils.camera import camera
from modules.utils.logout import logout
from modules.player_data.check_run import click_run
import time
import random
import re

# Corrected widget ID for equipment tab based on RuneLite API
EQUIPMENT_TAB_WIDGET_ID = '35913796'
EQUIPMENT_TAB_SELECTED_SPRITE_ID = 1030

def get_slayer_monster_name(widget_id=15138822) -> str | None:
    """
    Extracts and returns only the monster name from the slayer task widget text.
    Handles both:
    - New task: e.g. "Your new task is to kill 27 Hill giants."
    - Current task reminder: e.g. "You're still hunting hill giants; you have 40 to go."
    Returns the monster name string or None if no match.
    """
    text = check_widget_text(widget_id)
    
    if not text:
        print("No text found in widget")
        return None
    
    text = text.strip().lower()  # Normalize to lowercase for easier matching
    
    # Pattern 1: New task ("Your new task is to kill ..." or just "to kill ...")
    match = re.search(r'(?:new task is to kill|to kill)\s*\d+\s+(.+?)(?:\.)?$', text)
    if match:
        monster_name = match.group(1).strip()
        # Capitalize properly for consistency (Title Case)
        monster_name = monster_name.title()
        print("Task detected (new or reminder).", monster_name)
        return monster_name
    
    # Pattern 2: Current task reminder ("You're still hunting ...")
    match = re.search(r"still hunting\s+(.+?); you have \d+ to go", text)
    if match:
        monster_name = match.group(1).strip()
        monster_name = monster_name.title()
        print("Task detected (current reminder).", monster_name)
        return monster_name
    
    # Fallback pattern: any mention of assigned/kill/hunting a monster
    match = re.search(r"(?:assigned to kill|hunting)\s+(.+?)(?:\.|;|$)", text)
    if match:
        monster_name = match.group(1).strip()
        monster_name = monster_name.title()
        print("Task detected (fallback pattern).", monster_name)
        return monster_name
    
    print(f"Could not parse monster name from text: {text}")
    return None

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
        print("Failed to select Edgeville teleport on Amulet of Glory. trying inventory")
        for i in range(5):
            if click_lowest_glory(action='Rub'):
                break
            wait_for_next_tick()
            if i == 4:
                exit("Failed to click jewelry: Amulet of glory (Rub)")

        # 2
        # parent id: 14352385
        for i in range(5):
            if click_widget_child('14352385', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
                break
            wait_for_next_tick()
            if i == 4:
                exit("Failed to click dialogue option (edgeville) via child")
    


    print("Selected Edgeville teleport.")

    # Wait for tile change (teleport completion)
    tile_changed = wait_for_tile_change(timeout_ticks=20)
    if tile_changed:
        print("Teleport successful: Tile has changed.")
        # Adjust camera after teleport
        camera_adjusted = camera(pitch=319, yaw=1927, zoom=200)
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
    2. Enable run and toggle quick-prayers on/off.
    3. Wait until character stops moving.
    4. Handle door (1579 'Open') and ladder (1581 'Climb-down') in a simple loop:
       - Prioritizes 'Climb-down' if available.
       - Opens door if only 'Open' is available.
       - Exits loop only when neither option is visible (successfully below).
    5. Wait until on tile (3096, 9867, plane=0).
    Returns True if all steps successful, False otherwise.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Step 1: Click minimap tile + enable run
    clicked = click_minimap_tile(3094, 3470, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile.")
        return False
    print("Clicked minimap tile (3094, 3470).")
    click_run(enable=True)

    # Toggle quick-prayers on then off (refresh)
    for i in range(5):
        if click_widget('10485780', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()
        # if i == 4:
        #     exit("Failed to activate quick-prayers")

    for i in range(5):
        if click_widget('10485780', action='deactivate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()
        # if i == 4:
        #     exit("Failed to deactivate quick-prayers")

    # Step 2: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after minimap click.")
        return False
    wait_for_next_tick(2)

    # Steps 3-5: Simple loop for door + ladder
    max_attempts = 50  # Safety limit
    for attempt in range(1, max_attempts + 1):
        print(f"Dungeon entry attempt {attempt}/{max_attempts}")

        climb_obj = get_closest_object('1581', 'Climb-down')
        open_obj = get_closest_object('1579', 'Open')

        # Success: neither object visible → we're below
        if not climb_obj and not open_obj:
            print("Neither 'Climb-down' nor 'Open' found - successfully entered dungeon.")
            break

        # Prioritize Climb-down
        if climb_obj:
            print("'Climb-down' available - clicking")
            if click_object('1581', 'Climb-down'):
                print("Clicked Climb-down")
                wait_till_character_stopped_moving()
                wait_for_tick(ticks=random.randint(2, 4))
            else:
                print("Failed to click Climb-down")
                wait_for_tick(3)

        # Fallback to Open if trapdoor is closed
        elif open_obj:
            print("trapdoor closed - clicking Open")
            if click_object('1579', 'Open'):
                print("Clicked Open")
                wait_till_character_stopped_moving()
                wait_for_tick(ticks=random.randint(3, 6))
            else:
                print("Failed to click Open")
                wait_for_tick(3)

        else:
            wait_for_tick(1)

    else:
        print("Max attempts reached - failed to enter dungeon.")
        return False

    # Final confirmation: wait until on target tile
    reached = wait_for_specific_tile(3096, 9867, 0)
    if not reached:
        print("Failed to reach target tile (3096, 9867, 0)")
        return False

    print("Navigation to dungeon entrance completed successfully.")
    return True
def navigate_dungeon() -> str | None:
    """
    Navigates within the dungeon after reaching (3096, 9867):
    1. Click minimap tile (3095, 9902).
    2. Wait until character stops moving.
    3. Check if object 1568 with "Open" exists; if so, click it with "Open".
    4. Click minimap tile (3129, 9911).
    5. Wait until character stops moving.
    6. Click minimap tile (3145, 9913).
    7. Wait until character stops moving.
    8. Click NPC 'Vannaka' with 'Assignment'.
    9. Handle first-task dialogue if needed.
    10. Parse and return the assigned task name.
    Returns the task name string or None on failure.
    """
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return None

    # Step 1: Click minimap tile (3095, 9902)
    clicked = click_minimap_tile(3095, 9902, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3095, 9902).")
        return None
    print("Clicked minimap tile (3095, 9902).")

    # Step 2: Wait until stopped moving
    stopped = wait_till_character_stopped_moving(required_idle_ticks=2)
    if not stopped:
        print("Timeout waiting for character to stop moving after first dungeon minimap click.")
        return None

    # Step 3: Check and click object 1568 with "Open" if exists
    if click_object("1568", 'open', radius=20):
        print("Clicked object 1568 with 'Open'.")
        stopped = wait_till_character_stopped_moving()
        if not stopped:
            print("Timeout waiting for character to stop moving after opening object 1568.")
            return None
    else:
        print("Object 1568 with 'Open' not found; proceeding.")

    # Step 4: Click minimap tile (3129, 9911)
    clicked = click_minimap_tile(3129, 9911, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3129, 9911).")
        return None
    print("Clicked minimap tile (3129, 9911).")

    # Step 5: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after second dungeon minimap click.")
        return None

    # Step 6: Click minimap tile (3145, 9913)
    clicked = click_minimap_tile(3145, 9913, target_zoom=2.0)
    if not clicked:
        print("Failed to click minimap tile (3145, 9913).")
        return None
    print("Clicked minimap tile (3145, 9913).")

    # Step 7: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after third dungeon minimap click.")
        return None

    wait_for_tick(ticks=random.randint(3, 15))
    
    # Step 8: Click NPC 'Vannaka' with 'Assignment'
    npc_clicked = click_npc('Vannaka', 'Assignment')
    if not npc_clicked:
        print("Failed to click NPC Vannaka with 'Assignment'.")
        return None
    
    # Check if first task 
    first_task = False
    for _ in range(5):
        check_first_time = check_widget_text('14221318')  # Who are you?
        if check_first_time is None:
            print("Widget text 'Who are you?' not found, retrying...")
            wait_for_next_tick()
        else:
            first_task = True
            break

    if first_task:
        while True:
            keyboard.press('space')
            time.sleep(random.uniform(0.039, 0.081))
            keyboard.release('space')
            wait_for_next_tick()
            if check_widget_text('14352385', child_index=1) == 'Got any tips for me?':
                first_task = False
                break
            else:
                click_widget_child(id_str=14352385, child_index=1)

    # ← Changed: capture the task name instead of just calling the function
    task_name = get_slayer_monster_name()
    
    # wait_for_tick(ticks=random.randint(3, 50))
    # logout()  # Logs out after getting the task – perfect for the orchestrator
    return task_name  # ← Changed: return the task name (or None)

def full_navigation() -> str | None:
    """
    Performs the full sequence: Teleport to Edgeville, navigate to dungeon entrance,
    then navigate within the dungeon to get the task from Vannaka.
    Returns the assigned task name (str) or None on failure.
    """
    if not teleport_to_edgeville():
        return None
    
    if not navigate_to_dungeon():  # Entrance navigation
        return None
    
    task_name = navigate_dungeon()  # ← Fixed: removed duplicate call, now captures the task name
    print("Full navigation sequence completed.")
    return task_name  # ← Changed: return the task name or None

# Example usage: Run the full navigation
if __name__ == "__main__":
    full_navigation()