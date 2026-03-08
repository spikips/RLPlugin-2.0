import threading
import time
import pyautogui
import random
from modules.utils.inventory import click_inventory, get_inventory_count
from modules.utils.wait_for_tick import wait_for_tick
from modules.object_data.game_object import click_gameobject
from modules.core.plugin_client import players, game_state, pick, player, game_object, interact_options, bank_items, gear, inventory
from modules.widgets.widget import click_widget, click_widget_child, check_widget_text
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.utils.check_if_in_area import check_if_in_area
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.select_menu_option import select_menu_option
from modules.utils.camera import camera
from modules.core.mouse_control import move
from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.click_equipment import click_equipment_item
from modules.utils.banking import bank
from modules.object_data.object import click_object, check_object
from modules.core.plugin_client import gametick
from modules.utils.hop import logout_widget, quickhop_widget, get_hop_worlds, click_scrollbar, reset_quickhop
from modules.player_data.get_level import get_level
from modules.utils.logout import logout

TARGET_PRAYER_LEVEL = 77

hopping = False  # Shared global flag to pause/resume main loop
has_dragon_bones = True  # Track if we still have dragon bones (updated in main loop)
hop_coordinates = None  # Cache for hop click coordinates (screen_x, screen_y)

lumbridge_area = [
    "3214,3221,0",
    "3214,3211,0",
    "3227,3211,0",
    "3227,3226,0",
    "3217,3226,0",
    "3214,3221,0"
]

castle_wars_area = [
    "2434,3099,0",
    "2434,3080,0",
    "2446,3080,0",
    "2446,3099,0",
    "2434,3099,0"
]

lava_maze_area = [
    "3033,3846,0", "3023,3846,0", "3033,3813,0", "2944,3810,0", "2945,3820,0",
    "2946,3818,0", "2947,3818,0", "2948,3817,0", "2950,3815,0", "2952,3816,0",
    "2953,3818,0", "2958,3818,0", "2958,3823,0", "2954,3823,0", "2953,3824,0",
    "2953,3825,0", "2948,3825,0", "2946,3822,0", "2946,3827,0", "2992,3827,0",
    "3008,3839,0", "3023,3841,0", "3023,3846,0"
]

inside_altar_area = [
    "2947,3821,0",
    "2947,3819,0",
    "2948,3819,0",
    "2949,3818,0",
    "2949,3817,0",
    "2952,3817,0",
    "2952,3818,0",
    "2953,3819,0",
    "2956,3819,0",
    "2956,3822,0",
    "2953,3822,0",
    "2952,3823,0",
    "2952,3824,0",
    "2949,3824,0",
    "2949,3823,0",
    "2947,3821,0"
]

def check_prayer_level_and_stop():
    if TARGET_PRAYER_LEVEL is None:
        return
    try:
        current = get_level('prayer')
        if current >= TARGET_PRAYER_LEVEL:
            print("Prayer level " + str(current) + " reached target " + str(TARGET_PRAYER_LEVEL) + "! Logging out and stopping...")
            logout()
            time.sleep(1.5)
            exit(0)
    except Exception:
        pass

def is_player_dead():
    p_data = player(health=True)
    if p_data and 'data' in p_data:
        health = p_data['data'].get('health', 99)
        health_ratio = p_data['data'].get('healthRatio', 100)
        return health <= 0 or health_ratio == 0
    return False

def get_player_tile():
    p_data = player(location=True)
    if p_data and 'data' in p_data and 'location' in p_data['data']:
        loc = p_data['data']['location']
        return (loc['x'], loc['y'])
    return None

def tile_distance(t1, t2):
    """
    Calculate Euclidean distance between two tiles.
    """
    if t1 is None or t2 is None:
        return float('inf')
    dx = t1[0] - t2[0]
    dy = t1[1] - t2[1]
    return (dx**2 + dy**2)**0.5

def wait_until_stopped(max_ticks: int = 30):
    """
    Wait until the player's tile has not changed for 1 tick.
    Returns True if stopped within max_ticks, False otherwise.
    Also monitors for players during waiting and hops if necessary.
    """
    global hop_coordinates
    current_tile = get_player_tile()
    if current_tile is None:
        print("Failed to get initial player tile for stop check.")
        return False

    ticks_waited = 0
    while ticks_waited < max_ticks:
        wait_for_tick(1)
        new_tile = get_player_tile()
        if new_tile == current_tile:
            print("Character has stopped moving.")
            return True
        
        # Monitor for players during movement
        if check_if_in_area(lava_maze_area) or check_if_in_area(inside_altar_area):
            player_data = players(radius=15)
            if player_data and 'data' in player_data and len(player_data['data']) > 0:
                print(f"Players detected during movement: {len(player_data['data'])}, hopping...")
                if hop_coordinates is None:
                    quickhop_widget()
                    logout_widget()
                    worlds = get_hop_worlds()
                    if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
                        hop_coordinates = (worlds['screen_x'], worlds['screen_y'])
                    else:
                        print("Failed to get hop coordinates.")
                        # Fail safe, assume hopped
                        return False
                if hop_coordinates:
                    move(hop_coordinates[0], hop_coordinates[1], button='left', fast=True, sleep=True)
                wait_for_tick(3)
                while True:
                    state = game_state()
                    if state['data'] == 'LOGGED_IN':
                        time.sleep(0.1)
                        print("Logged in after hop, clicking scrollbar.")
                        click_scrollbar()
                        break
                # Reset cache after successful hop/login
                hop_coordinates = None
                # After hop, restart the stop check
                return False
        
        current_tile = new_tile
        ticks_waited += 1
        print(f"Character still moving, waited {ticks_waited} ticks.")

    print(f"Character did not stop moving after {max_ticks} ticks.")
    return False

def perform_hop():
    """
    Perform world hop and wait for login.
    Returns True if successful hop and login.
    """
    global hop_coordinates
    if hop_coordinates is None:
        quickhop_widget()
        logout_widget()
        worlds = get_hop_worlds()
        if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
            hop_coordinates = (worlds['screen_x'], worlds['screen_y'])
        else:
            print("Failed to get hop coordinates.")
            return False
    if hop_coordinates:
        move(hop_coordinates[0], hop_coordinates[1], button='left', fast=True, sleep=True)
    wait_for_tick(3)
    while True:
        state = game_state()
        if state['data'] == 'LOGGED_IN':
            time.sleep(0.1)
            print("Logged in after hop, clicking scrollbar.")
            click_scrollbar()
            break
    hop_coordinates = None
    return True

def use_bone():
    """
    Attempt to use a dragon bone on the chaos altar up to 3 times.
    """
    success = False
    for attempt in range(3):
        print(f"Attempting to use bone {attempt + 1}/3")
        pyautogui.press('f1')  # Open inventory
        if click_inventory('dragon bones'):
            print('Clicked dragon bones')
            if click_gameobject('chaos altar', action='use'):
                print("Used bone on altar. pressing f5 to open logout widget")
                pyautogui.press('f5')

                if quickhop_widget():
                    pyautogui.press('f1')  # Open inventory
                    wait_for_tick(1)
                    if click_inventory('dragon bones'):
                        print('Clicked dragon bones')
                        if click_gameobject('chaos altar', action='use'):
                            print("Used bone on altar. pressing f5 to open logout widget")
                            pyautogui.press('f5')
                            
                success = True
                return success
            else:
                print('No altar found')
        wait_for_tick(1)
    if not success:
        print("Failed to use bone after 3 attempts, continuing to next check.")
        return success

def open_bank():
    # Find bank chest with a broader tile radius
    bank_obj = game_object("bank chest", tile_radius=15, middle_point=True)
    if not bank_obj or 'data' not in bank_obj or not bank_obj['data']:
        print("Failed to find bank chest. Dumping game_object data for debugging:")
        print(bank_obj)
        return False

    bank_item = bank_obj['data'][0]
    bank_canvas_x = bank_item.get('middle_point', {'x': 0, 'y': 0})['x']
    bank_canvas_y = bank_item.get('middle_point', {'x': 0, 'y': 0})['y']
    bank_screen_x, bank_screen_y = runelite_window(bank_canvas_x, bank_canvas_y)
    print(f"Found bank chest at canvas ({bank_canvas_x}, {bank_canvas_y}), screen ({bank_screen_x}, {bank_screen_y})")

    # Hover over the bank to check default action
    print(f"Hovering over bank at {bank_screen_x}, {bank_screen_y} (middle_point from game_object)")
    move(bank_screen_x, bank_screen_y, fast=True, sleep=True)  # Move mouse without clicking
    time.sleep(random.uniform(0.1, 0.2))

    # Get interact options (potential menu)
    options_data = interact_options()
    if not options_data or 'data' not in options_data or not options_data['data']:
        print("No interact options found after hovering")
        return False

    first_option = options_data['data'][0]['option'].lower()
    if 'bank' in first_option or 'use' in first_option:
        # Left-click directly
        print(f"Default action is '{first_option}', left-clicking at {bank_screen_x}, {bank_screen_y}")
        move(bank_screen_x, bank_screen_y, button='left')
    else:
        # Right-click and select 'Bank' or 'Use'
        print(f"Default action is not 'bank' or 'use' ({first_option}), right-clicking")
        move(bank_screen_x, bank_screen_y, button='right')
        time.sleep(random.uniform(0.1, 0.3))
        options_data = interact_options()  # Now with open menu
        if not options_data or 'data' not in options_data:
            print("Failed to retrieve bank chest interaction options after right-click.")
            return False

        bank_option = None
        for opt in options_data['data']:
            option_lower = opt.get('option', '').lower()
            if 'bank' in option_lower or 'use' in option_lower:
                bank_option = opt
                break

        if not bank_option:
            print("Bank/Use option not found in menu.")
            return False

        bank_option_x = bank_option['middle_point']['x']
        bank_option_y = bank_option['middle_point']['y']
        bank_option_screen_x, bank_option_screen_y = runelite_window(bank_option_x, bank_option_y)
        print(f"Selecting 'Bank/Use' from menu at canvas ({bank_option_x}, {bank_option_y}), screen ({bank_option_screen_x}, {bank_option_screen_y}) (middle_point from interact_options)")
        move(bank_option_screen_x, bank_option_screen_y, button='left', fast=True, sleep=True)

    max_attempts = 20  # ~12 seconds (each tick ~0.6s)
    for _ in range(max_attempts):
        bank_data = bank_items()
        if bank_data and 'data' in bank_data and bank_data['data'] is not None and len(bank_data['data']) > 0:
            print("Bank opened successfully.")
            return True
        wait_for_tick()

    print("Failed to open bank after waiting.")
    return False

def is_inside_altar():
    """
    Check if player is inside the chaos altar area.
    """
    return check_if_in_area(inside_altar_area)

def monitor_players_clear():
    """
    Monitor for players until clear.
    If players detected, hop and recheck.
    Returns True if clear to proceed.
    """
    global hop_coordinates
    while True:
        if check_if_in_area(lava_maze_area) or check_if_in_area(inside_altar_area):
            player_data = players(radius=15)
            if player_data and 'data' in player_data and len(player_data['data']) > 0:
                print(f"Players detected: {len(player_data['data'])}, hopping...")
                if hop_coordinates is None:
                    quickhop_widget()
                    logout_widget()
                    worlds = get_hop_worlds()
                    if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
                        hop_coordinates = (worlds['screen_x'], worlds['screen_y'])
                    else:
                        print("Failed to get hop coordinates.")
                        return True  # Fail safe, assume clear
                if hop_coordinates:
                    move(hop_coordinates[0], hop_coordinates[1], button='left', fast=True, sleep=True)
                wait_for_tick(3)
                while True:
                    state = game_state()
                    if state['data'] == 'LOGGED_IN':
                        time.sleep(0.1)
                        print("Logged in after hop, clicking scrollbar.")
                        click_scrollbar()
                        break
                # Reset cache after successful hop/login
                hop_coordinates = None
                # Recheck after hop
                player_data = players(radius=15)
                if not (player_data and 'data' in player_data and len(player_data['data']) > 0):
                    print("No players after hop, clear to proceed.")
                    return True
            else:
                print("No players detected, clear to proceed.")
                return True
        wait_for_tick(1)

def monitor_until_safe_or_hop():
    """
    Monitor for players after bone use until safe (no players for min_safe_ticks) or hop needed.
    Ensures minimum safe ticks before proceeding to next bone.
    Returns 'safe' if clear for sufficient consecutive ticks,
    'hopped' if hopped and clear, 'left_area' if left area, 'no_bones' if no bones left.
    """
    global hop_coordinates
    min_safe_ticks = 3  # Minimum ticks without players to consider safe for next bone
    safe_ticks = 0
    while True:
        bone_count = get_inventory_count('Dragon bones')
        if bone_count == 0:
            print("No more dragon bones during monitoring.")
            return 'no_bones'
        # if not (check_if_in_area(inside_altar_area)):
        #     print("Left the area during monitoring.")
        #     return 'left_area'
        player_data = players(radius=12)
        num_players = len(player_data['data']) if player_data and 'data' in player_data else 0
        if num_players > 0:
            safe_ticks = 0  # Reset safe counter on player detection
            print(f"Players detected ({num_players}), hopping...")
            if hop_coordinates is None:
                print('no hop coordinates')

                while not get_hop_worlds():
                    quickhop_widget()
                    logout_widget()
                worlds = get_hop_worlds()

                if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
                    hop_coordinates = (worlds['screen_x'], worlds['screen_y'])

            if hop_coordinates:
                for _ in range(2):
                    move(hop_coordinates[0], hop_coordinates[1], button='left', fast=True, sleep=True)
            wait_for_tick(3)
            while True:
                state = game_state()
                if state['data'] == 'LOGGED_IN':
                    time.sleep(0.1)
                    print("Logged in after hop, clicking scrollbar.")   
                    click_scrollbar()
                    break
            # Reset cache after successful hop/login
            hop_coordinates = None
            # Recheck after hop
            wait_for_tick(1)
            player_data = players(radius=12)
            num_players_after = len(player_data['data']) if player_data and 'data' in player_data else 0
            if num_players_after == 0:
                print("Cleared after hop.")
                return 'hopped'
            else:
                print(f"Still {num_players_after} players after hop, continuing hopping")
                if hop_coordinates is None:
                    print('no hop coordinates')
                    quickhop_widget()
                    logout_widget()
                    worlds = get_hop_worlds()
                    if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
                        hop_coordinates = (worlds['screen_x'], worlds['screen_y'])
                    else:
                        print("Failed to get hop coordinates.")
                            
                if hop_coordinates:
                    for _ in range(2):
                        move(hop_coordinates[0], hop_coordinates[1], button='left', fast=True, sleep=True)
                wait_for_tick(3)
                # After second hop, return 'hopped' to break and re-enter main logic
                return 'hopped'
        else:
            # No players, increment safe ticks
            safe_ticks += 1
            print(f"No players detected, safe ticks: {safe_ticks}/{min_safe_ticks}")
            if safe_ticks >= min_safe_ticks:
                print("Sufficient safe ticks reached, ready for next bone.")
                return 'safe'
        wait_for_tick(1)


def move_to_optimal_tile(zoom_level=4):
    """
    Move to the optimal tile 2948, 3821 using minimap click with specified zoom.
    Click twice for reliability.
    Wait until stopped.
    """
    waypoint = (2948, 3821)
    attempts = 0
    max_attempts = 3
    while attempts < max_attempts:
        success = False
        for _ in range(15):
            if click_minimap_tile(*waypoint, target_zoom=zoom_level):
                success = True
                # Click again for double-click
                click_minimap_tile(*waypoint, target_zoom=zoom_level)
                break
            wait_for_tick(1)
        if success:
            if wait_until_stopped():
                current_tile = get_player_tile()
                if current_tile and tile_distance(current_tile, waypoint) <= 5:
                    print("Moved to optimal tile 2948, 3821 and stopped within range.")
                    # Monitor for clear players before proceeding
                    if monitor_players_clear():
                        return True
                    else:
                        print("Cannot proceed, retrying move.")
                else:
                    print(f"Not close enough to optimal tile (distance {tile_distance(current_tile, waypoint) if current_tile else 'inf'}), retrying.")
            else:
                print("Moved to optimal tile but did not stop.")
        attempts += 1
        wait_for_tick(1)
    print("Failed to move to optimal tile 2948, 3821 after max attempts.")
    return False

def open_door_if_needed():
    """
    Open the door (ID 1524) by checking if object exists and clicking every 6 ticks until no object found.
    Monitors for players before clicking and during the wait ticks, hopping if necessary.
    """
    print('opening door')
    # Initial clear check
    if not monitor_players_clear():
        print("Cannot start door opening.")
        return False

    max_attempts = 5
    for attempt in range(max_attempts):
        # Monitor players before clicking
        if not monitor_players_clear():
            print(f"Players detected before clicking door on attempt {attempt + 1}, hopping and retrying.")
            perform_hop()
            # After hop, ensure clear before retrying click
            if not monitor_players_clear():
                print("Still not clear after hop before door click.")
                return False
            continue  # Retry the click

        # Try to click the door
        door_open = False
        while True:
            door = click_object('1524', 'open')
            for tick in range(6):
                if not check_object('1524', 'open'):
                    door_open = True
                    break  # Door opened, exit wait early
                wait_for_tick(1)
            if door_open:
                break  # Exit the attempt loop if door opened

        if not door:
            print("door open")
            wait_for_tick(1)
            print("Waited one tick after confirming door open.")
            # If door is open but not inside altar, move to optimal tile
            if not is_inside_altar():
                print("Door open but not inside altar, clicking minimap tile 2948, 3821.")
                return move_to_optimal_tile(zoom_level=4)
            print("Door open and inside altar, proceeding.")
            return True

        # Door found and clicked, wait 6 ticks with player monitoring
        print(f"Clicked door on attempt {attempt + 1}, waiting 6 ticks with monitoring.")
        interrupted = False
        for tick in range(6):
            if not check_object('1524', 'open'):
                break  # Door opened, exit wait early
            wait_for_tick(1)
            # Check players after each tick
            if check_if_in_area(lava_maze_area) or check_if_in_area(inside_altar_area):
                player_data = players(radius=15)
                num_players = len(player_data['data']) if player_data and 'data' in player_data else 0
                if num_players > 0:
                    print(f"Players detected ({num_players}) during door wait on tick {tick + 1}, hopping.")
                    perform_hop()
                    # After hop, ensure clear
                    if monitor_players_clear():
                        print("Clear after hop during door wait, but animation interrupted; retrying door click.")
                        interrupted = True
                        break
                    else:
                        print("Still not clear after hop during door wait.")
                        return False

        if interrupted:
            continue  # Retry the outer attempt (re-click door)

    print("Door did not open after max click attempts.")
    return False

def navigate_from_lava_maze():
    """
    Navigate from Lava Maze to the Chaos Altar using dynamic waypoint selection based on current position.
    Then open door if needed, then move to optimal tile.
    """
    global hop_coordinates
    hop_coordinates = None  # Reset before potential hop
    quickhop_widget()
    logout_widget()
    # worlds = get_hop_worlds()
    # if worlds and 'screen_x' in worlds and 'screen_y' in worlds:
    #     move(worlds['screen_x'], worlds['screen_y'], button='left', fast=True, sleep=True)
    
    # wait_for_tick(3)
    # while True:
    #     state = game_state()
    #     if state['data'] == 'LOGGED_IN':
    #         time.sleep(0.1)
    #         click_scrollbar()
    #         break
    waypoints = [(3006, 3821), (2976, 3820), (2959, 3820)]
    current_tile = get_player_tile()
    if current_tile is None:
        print("Could not get current tile, using full waypoint path.")
        sub_waypoints = waypoints
    else:
        dists = [tile_distance(current_tile, wp) for wp in waypoints]
        min_idx = dists.index(min(dists))
        sub_waypoints = waypoints[min_idx:]
        print(f"Current tile {current_tile}, distances: {dists}, starting from waypoint index {min_idx}: {sub_waypoints}")

    all_success = True
    for waypoint in sub_waypoints:
        attempts = 0
        max_attempts = 3
        waypoint_reached = False
        while attempts < max_attempts and not waypoint_reached:
            success = False
            for _ in range(15):
                if click_minimap_tile(*waypoint, target_zoom=2):
                    success = True
                    break
                wait_for_tick(1)
            if success:
                if wait_until_stopped():
                    current_tile = get_player_tile()
                    if current_tile and tile_distance(current_tile, waypoint) <= 5:
                        print(f"Reached waypoint {waypoint} within range.")
                        # Monitor for clear players before proceeding to next
                        if monitor_players_clear():
                            waypoint_reached = True
                        else:
                            print("Cannot proceed, retrying waypoint.")
                    else:
                        print(f"Not close enough to waypoint {waypoint} (distance {tile_distance(current_tile, waypoint) if current_tile else 'inf'}), retrying.")
                else:
                    print(f"Character did not stop after waypoint {waypoint}.")
            attempts += 1
        if not waypoint_reached:
            all_success = False
            print(f"Failed to reach waypoint {waypoint} after max attempts.")
            break
    if all_success:
        print("All waypoints navigated successfully, opening door if needed.")
        if open_door_if_needed():
            print("Door handled.")
            # Only move to optimal if not already handled in open_door_if_needed
            if not is_inside_altar():
                return move_to_optimal_tile(zoom_level=4)
            return True
    return False


while True:
    check_prayer_level_and_stop()
    if check_if_in_area(lumbridge_area):
        reset_quickhop()
        print("In Lumbridge, handling teleport to Castle Wars.")
        wait_for_tick(1)  # Allow time for respawn to fully load
        # Check for ring of dueling in inventory first (try variants)
        ring_clicked = False
        for charge in range(1, 9):  # 1 to 8 charges
            ring_name = f'ring of dueling({charge})'
            if click_inventory(ring_name):
                ring_clicked = True
                print(f"Clicked {ring_name} from inventory (equipped).")
                break
        
        if ring_clicked:
            wait_for_tick(2)
            focus_runelite_window()
            pyautogui.press('escape')  # Open equipment
            time.sleep(0.1)  # Brief pause for UI to open
            click_equipment_item("Ring of dueling", "Castle Wars")
            if wait_for_tile_change():
                print("Tile changed after teleport, setting camera.")
                # Now that we're in Castle Wars, the main loop will handle the rest via the area check
            else:
                print("Tile did not change after teleport attempt.")
            
            # If still in Lumbridge after handling, end session
            if check_if_in_area(lumbridge_area):
                print("Still in Lumbridge after teleport attempt, ending session.")
                exit()
        else:
            print("No ring of dueling in inventory, attempting widget teleport to Castle Wars.")
            for i in range(7):
                click_widget('35913776', rand_x=10, rand_y=10)
                wait_for_tick(1)
                click_widget('46333957', rand_x=10, rand_y=10)
                wait_for_tick(1)
                click_widget('35913776')
                wait_for_tick(1)
                click_widget('4980746', rand_x=50, rand_y=5)
                wait_for_tick(1)

                # 4980758       
                for child in range(8):
                    castle_wars = check_widget_text('4980758', child_index=child)
                    if castle_wars and 'castle wars' in castle_wars.lower():
                        print('clicking castle wars widget')
                        click_widget_child('4980758', child_index=child)
                        break

                time.sleep(0.3)
                click_widget('4980768', rand_x=5, rand_y=5)

                if wait_for_tile_change(timeout_ticks=40):
                    print("Successfully teleported to Castle Wars using widgets.")
                    break
                print(f'unable to teleport to castle wars, sleeping for 3-4min and retrying {i}')
                time.sleep(random.randint(3,4)*60)
            # If still in Lumbridge after widget attempts, end session
            if check_if_in_area(lumbridge_area):
                print("Still in Lumbridge after widget teleport attempts, ending session.")
                exit()
        continue

    if check_if_in_area(castle_wars_area):
        print("In Castle Wars area, checking equipment and inventory.")
        focus_runelite_window()
        camera(413, 1662, 294)
        gear_data = gear()
        amulet_equipped = gear_data and 'data' in gear_data and any('burning amulet' in name.lower() for name in gear_data['data'].keys())
        ring_equipped = gear_data and 'data' in gear_data and any('ring of dueling' in name.lower() for name in gear_data['data'].keys())
        bones_count = get_inventory_count('Dragon bones')
        if amulet_equipped and ring_equipped and bones_count == 28:
            print("All set, teleporting to Lava Maze.")
            pyautogui.press('escape')  # Close inventory
            time.sleep(0.1)
            click_equipment_item("Burning amulet", "Lava maze")
            print("Used Lava maze on burning amulet.")
            wait_for_tick(1)
            for _ in range(1, random.randint(4, 5)):
                pyautogui.press('1')
                time.sleep(random.uniform(0.16, 0.2))
            if wait_for_tile_change():
                camera(320, 756, 283)
                print("Teleported to lava maze, clicking first waypoint.")
                click_minimap_tile(3006, 3821, target_zoom=2)
                print("Navigating to chaos altar.")
                navigate_from_lava_maze()
                has_dragon_bones = True
            else:
                print("Tile did not change after teleport attempt.")
        else:
            print(f"Missing items: amulet={amulet_equipped}, ring={ring_equipped}, bones={bones_count}/28")
            pyautogui.press('escape')  # Close inventory
            time.sleep(0.1)
            if open_bank():
                print("Bank opened at Castle Wars.")
                # Equip burning amulet if not equipped
                if not amulet_equipped:
                    # Try to equip from inventory first
                    amulet_from_inv = False
                    for charge in range(1, 6):  # 1 to 5 charges
                        amulet_name = f'burning amulet({charge})'
                        if click_inventory(amulet_name, action='wear'):
                            print(f"Equipped {amulet_name} from inventory.")
                            amulet_from_inv = True
                            break
                    
                    if not amulet_from_inv:
                        print("No burning amulet in inventory, withdrawing from bank.")
                        bank(withdraw='burning amulet(5)', quantity=1, deposit_inventory=True)
                        wait_for_tick(2)
                        click_inventory('burning amulet(5)', action='Wear')
                        print("Equipped burning amulet(5) from bank.")
                
                # Equip ring if not equipped
                if not ring_equipped:
                    # Withdraw ring of dueling(8) if not equipped
                    print("No ring of dueling equipped, withdrawing from bank.")
                    bank(withdraw='ring of dueling(8)', quantity=1, deposit_inventory=True)
                    wait_for_tick(2)
                    # Wear it
                    click_inventory('ring of dueling(8)', action='wear')
                    print("Equipped ring of dueling(8) from bank.")
                
                # Withdraw dragon bones to fill inventory
                if bones_count < 28:
                    print("Withdrawing dragon bones (all) and depositing inventory.")
                    bank(withdraw='dragon bones', quantity='all', deposit_inventory=True)
                    has_dragon_bones = True  # Now have bones again, enable monitoring
                
                # Close bank
                focus_runelite_window()
                for _ in range(random.randint(4, 5)):
                    pyautogui.press('escape')
                    time.sleep(random.uniform(0.15, 0.2))
            else:
                print("Failed to open bank.")
        continue

    if not check_if_in_area(lumbridge_area) and not check_if_in_area(castle_wars_area) and not check_if_in_area(lava_maze_area) and not check_if_in_area(inside_altar_area):
        print("In unknown location, attempting to teleport to Castle Wars using widgets.")
        for i in range(7):
            click_widget('35913776', rand_x=10, rand_y=10)
            time.sleep(0.3)
            click_widget('46333957', rand_x=10, rand_y=10)
            time.sleep(0.3)
            click_widget('35913776')
            time.sleep(0.3)
            click_widget('4980746', rand_x=50, rand_y=5)
            time.sleep(0.3)

            # 4980758       
            for child in range(8):
                castle_wars = check_widget_text('4980758', child_index=child)
                if castle_wars and 'castle wars' in castle_wars.lower():
                    print('clicking castle wars widget')
                    click_widget_child('4980758', child_index=child)
                    break

            time.sleep(0.3)
            click_widget('4980768', rand_x=5, rand_y=5)

            if wait_for_tile_change(timeout_ticks=40):
                print("Successfully teleported to Castle Wars using widgets.")
                break
            print(f'unable to teleport to castle wars, sleeping for 3-4min and retrying {i}')
            time.sleep(random.randint(3,4)*60)
        continue

    if has_dragon_bones:
        # === STRONG DEATH / LUMBRIDGE CHECK FIRST ===
        if is_player_dead() or check_if_in_area(lumbridge_area):
            reset_quickhop()
            print("Detected death or Lumbridge respawn while we still have bones.")
            has_dragon_bones = False
            continue

        inside_altar = is_inside_altar()
        if not inside_altar:
            if check_if_in_area(lava_maze_area):
                print("In lava maze area, navigating to altar.")
                navigate_from_lava_maze()
            else:
                print("Not in expected area, skipping navigation.")
            inside_altar = is_inside_altar()

        if inside_altar:
            camera(465, 1192, 1448)

            if monitor_players_clear():
                bone_count = get_inventory_count('Dragon bones')
                if bone_count > 0:
                    if use_bone():
                        check_prayer_level_and_stop()
                        while True:
                            result = monitor_until_safe_or_hop()
                            if result == 'no_bones':
                                has_dragon_bones = False
                                print("No more dragon bones.")
                                break
                            elif result in ['hopped']:
                                use_bone()

                                # === CRITICAL FIX: Check if we actually died and respawned ===
                            if is_player_dead() or check_if_in_area(lumbridge_area):
                                reset_quickhop()
                                print("Detected Lumbridge respawn after being killed during hop!")
                                has_dragon_bones = False
                                break
                    else:
                        if is_player_dead() or check_if_in_area(lumbridge_area):
                            reset_quickhop()
                            print("Respawned in Lumbridge after failed bone use.")
                            has_dragon_bones = False
                            break
                else:
                    has_dragon_bones = False
        else:
            print("Failed to reach inside altar, skipping bone use.")

    else:
        # === IMPROVED SUICIDE MODE (already has Lumbridge check every cycle) ===
        print('no more dragon bones')
        print("Entering suicide mode with Wine of Zamorak...")

        if check_if_in_area(lumbridge_area):
            reset_quickhop()
            print("Already in Lumbridge - skipping suicide completely.")
            continue

        camera(512, 2017, 534)

        suicide_attempts = 0
        max_suicide_attempts = 300

        while True:
            check_prayer_level_and_stop()
            suicide_attempts += 1
            if suicide_attempts > max_suicide_attempts:
                print("Suicide mode timeout reached.")
                break

            if check_if_in_area(lumbridge_area) or is_player_dead():
                print("Detected Lumbridge respawn during suicide mode.")
                reset_quickhop()
                break

            # Click wine 3x per cycle
            wine_picked = False
            for _ in range(3):
                wine_data = pick(2950, 3824, size=10, item='Wine of zamorak')
                if suicide_attempts < 1:
                    wait_for_tick(2)
                if wine_data and 'data' in wine_data and wine_data['data'].get('items'):
                    wine_item = wine_data['data']['items'][0]
                    if 'middle_point' in wine_item:
                        select_menu_option(wine_item['middle_point']['x'], wine_item['middle_point']['y'], 'Take')
                        time.sleep(random.uniform(0.04, 0.09))
                        wine_picked = True
                        break
                time.sleep(random.uniform(0.04, 0.07))

            if not wine_picked and suicide_attempts % 20 == 0:
                print(f"No wine found on attempt {suicide_attempts}")

            time.sleep(0.08)

        # Confirm we are really in Lumbridge
        print("Waiting to confirm Lumbridge respawn...")
        while not check_if_in_area(lumbridge_area):
            reset_quickhop()
            wait_for_tick(1)
        print("Successfully back in Lumbridge.")
        continue