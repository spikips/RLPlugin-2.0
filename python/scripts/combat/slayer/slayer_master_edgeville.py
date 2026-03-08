# slayer_master_edgeville.py
# A script for navigating to the Slayer Master Vannaka in Edgeville Dungeon in Old School RuneScape via RuneLite plugin.
import keyboard
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.utils.automatic_scripting.small_functions import click_lowest_glory
from modules.utils.check_if_in_tile import check_if_in_tile
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
from scripts.combat.slayer.utils.skip_task import skip_current_task
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

def parse_slayer_task_from_widget(widget_id: str = "15138822") -> tuple[str | None, int | None]:
    """Parse monster name + amount from Vannaka's first-task dialogue (widget 15138822).
    Handles exactly: "We'll start you off hunting ghouls, you'll need to kill 14<br>of them."
    Bigger picture: captures initial kill count the moment dialogue appears (before any skip/loop)."""
    try:
        raw = check_widget_text(widget_id)
        if not raw:
            return None, None
        text = raw.replace("<br>", " ").replace("\n", " ").strip().lower()
        match = re.search(r"hunting ([\w\s]+?)(?:,|\s+you'll)", text)
        if match:
            monster = match.group(1).strip().title()
            amt_match = re.search(r"kill (\d+)", text)
            amount = int(amt_match.group(1)) if amt_match else None
            return monster, amount
        match2 = re.search(r"kill (\d+)\s+([\w\s]+?)(?=\.|$)", text)
        if match2:
            return match2.group(2).strip().title(), int(match2.group(1))
        return None, None
    except Exception:
        return None, None

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

    toggle_prayer('PROTECT_FROM_MELEE', activate=False)

    # Step 2: Wait until stopped moving
    stopped = wait_till_character_stopped_moving()
    if not stopped:
        print("Timeout waiting for character to stop moving after minimap click.")
        return False
    wait_for_next_tick(2)

    start_time = time.time()
    max_duration = 38.0

    while time.time() - start_time < max_duration:
        pos = get_player_position()

        # Success: underground and near target
        if pos and pos[2] == 0 and abs(pos[0] - 3096) <= 5 and abs(pos[1] - 9867) <= 5:
            print("Successfully entered dungeon.")
            break

        # Priority 1: Climb-down if available
        if get_closest_object('1581', 'Climb-down'):
            print("Climb-down available - clicking")
            if click_object('1581', 'Climb-down'):
                wait_till_character_stopped_moving()

        # Priority 2: Open trapdoor if closed
        elif get_closest_object('1579', 'Open'):
            print("Trapdoor closed - opening")
            if click_object('1579', 'Open'):
                wait_till_character_stopped_moving(required_idle_ticks=2)

        # Reposition if needed
        else:
            if pos and pos[2] == 0:  # Still on surface
                print("No object visible - walking closer")
                click_minimap_tile(3094, 3470, target_zoom=2.0)
            else:
                print("Walking to target tile inside dungeon")
                click_minimap_tile(3096, 9867, target_zoom=2.0)

    else:
        print("Dungeon entry timed out.")
        return False

    # Phase 3: Final precise positioning
    if check_if_in_tile(3096, 9867, plane=0, click=True, tile_radius=5):
        print("Precisely positioned at target tile (3096, 9867, 0)")
    else:
        print("Entered dungeon - approximate position reached")

    print("Dungeon navigation completed successfully.")
    return True

# slayer_master_edgeville.py
# Updated navigate_dungeon() – keeps your exact original tight sleep style (0.039-0.081) and structure
# Fix: captures task name DURING first-task dialogue (while widget 15138822 still exists)
# Falls back to get_slayer_monster_name() for normal tasks
# No generous sleeps, no big changes to navigation/gate handling

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
    9. Handle first-task dialogue if needed (tight original style).
    10. Return the assigned task name.
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
    stopped = wait_till_character_stopped_moving(required_idle_ticks=3)
    if not stopped:
        print("Timeout waiting for character to stop moving after first dungeon minimap click.")
        return None

    print("Handling dungeon gate 1568 and walking to tile (3129, 9911)")
    
    gate_start_time = time.time()
    max_gate_duration = 25.0

    while time.time() - gate_start_time < max_gate_duration:
        pos = get_player_position()

        if pos and abs(pos[0] - 3129) <= 6 and abs(pos[1] - 9911) <= 6:
            print(f"Successfully passed gate. Current position: {pos}")
            break

        if get_closest_object("1568", "Open", radius=25):
            print("Gate is closed - clicking Open")
            if click_object("1568", "Open", radius=25):
                wait_till_character_stopped_moving()
                continue

        print("Gate open - clicking minimap tile (3129, 9911)")
        clicked = click_minimap_tile(3129, 9911, target_zoom=2.0)
        if not clicked:
            print("Failed to click minimap tile (3129, 9911)")

        wait_till_character_stopped_moving()

    else:
        print("Warning: Timed out trying to pass gate. Continuing anyway.")

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
    
    # === First-task handling (exactly your original tight style) ===
    first_task = False
    for _ in range(5):
        check_first_time = check_widget_text('14221318')  # Who are you?
        if check_first_time is not None:
            first_task = True
            break
        wait_for_next_tick()

    parsed_name = None
    if first_task:
        print("First-task dialogue detected – using your tight space spam style")
        while True:
            keyboard.press('space')
            time.sleep(random.uniform(0.039, 0.081))
            keyboard.release('space')
            wait_for_next_tick()

            # Capture task name + amount WHILE widget is still visible
            name, amount = parse_slayer_task_from_widget("15138822")
            if name:
                parsed_name = name
                print(f"Got task from widget 15138822: {name} x {amount}")

            if check_widget_text('14352385', child_index=1) == 'Got any tips for me?':
                first_task = False
                click_widget_child(id_str=14352385, child_index=1)
                break
            else:
                click_widget_child(id_str=14352385, child_index=1)

    # Final capture – use parsed name if first-task succeeded, otherwise normal widget read
    task_name = parsed_name or get_slayer_monster_name()
    
    if task_name:
        print(f"Final task captured successfully: {task_name}")
        return task_name
    else:
        print("Failed to capture task name after dialogue.")
        return None

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

def full_navigation_with_skip_loop(tasks_to_skip: list[str] | None = None) -> str | None:
    """
    Performs the full sequence with task skipping loop:
    1. Teleport to Edgeville, navigate to dungeon entrance, navigate to Vannaka
    2. Get the assigned task
    3. If task is in skip list, click skip (Rewards → Tasks → Cancel) and loop back to step 2
    4. Return the accepted task name (or None if all attempts failed)
    """
    if tasks_to_skip is None:
        tasks_to_skip = []
    
    # Normalize skip list for comparison
    skip_list_normalized = [t.strip().lower().replace(" ", "_").replace("-", "_") for t in tasks_to_skip]
    
    max_skip_attempts = 10  # Prevent infinite loop if all available tasks are on skip list
    
    for skip_attempt in range(max_skip_attempts):
        print(f"\n=== Task assignment attempt {skip_attempt + 1} ===")
        
        # Navigate to Vannaka and get task
        if not teleport_to_edgeville():
            return None
        
        if not navigate_to_dungeon():  # Entrance navigation
            return None
        
        task_name = navigate_dungeon()  # Get the task
        if task_name is None:
            return None
        
        task_name = task_name.strip()
        print(f"Assigned task: '{task_name}'")
        
        # Check if task is on skip list
        normalized_task = task_name.strip().lower().replace(" ", "_").replace("-", "_")
        if normalized_task in skip_list_normalized:
            print(f"Task '{task_name}' is on skip list - skipping...")
            try:
                skip_current_task()
                wait_for_next_tick(2)
                print("Skipped task, requesting new assignment...")
                continue  # Loop back to get a new task
            except Exception as e:
                print(f"Failed to skip task: {e}")
                return None
        else:
            # Task accepted
            print(f"Task '{task_name}' accepted.")
            return task_name
    
    print(f"Exhausted {max_skip_attempts} skip attempts - all available tasks may be on skip list.")
    return None

# Example usage: Run the full navigation
if __name__ == "__main__":
    full_navigation()