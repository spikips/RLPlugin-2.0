import time
import random
import keyboard
from datetime import datetime, timedelta
from modules.core.plugin_client import inventory, bank_items, game_state, stats as plugin_stats, interact_options,gear , player, game_object, tile, walkable_tile
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window
from modules.utils.banking import bank, get_all_widget_data
from modules.utils.camera import camera
from modules.utils.logout import logout_and_break

rl_x, rl_y = runelite_window(0, 0)

# Track if initial items (tinderbox, law runes, fire runes, staff of air) have been withdrawn
initial_items_withdrawn = False

# Tile alternation flag
use_first_tile = True  # Start with first tile (3209, 3429)

def get_required_level(log_type):
    """Return the required Firemaking level for the log type."""
    levels = {
        "logs": 1,
        "oak logs": 15,
        "willow logs": 30,
        "maple logs": 45
    }
    return levels.get(log_type.lower(), 99)  # Default high if unknown

def withdraw_logs():
    """Attempt to withdraw logs in order if level sufficient; return True if successful, exit if no logs."""
    firemaking_level = plugin_stats().get('data', {}).get('Firemaking', {}).get('level', 0)
    print(f"Current Firemaking level: {firemaking_level}")

    log_types = ["logs", "oak logs", "willow logs", "maple logs"]
    for log_type in log_types:
        required_level = get_required_level(log_type)
        if firemaking_level >= required_level:
            if bank(withdraw=log_type, placeholder=True, quantity="all", noted=False):
                print(f"Withdrew {log_type}")
                return True
            else:
                print(f"No {log_type} found, trying next")
        else:
            print(f"Level {firemaking_level} insufficient for {log_type} (needs {required_level}), trying next")
    exit("No suitable logs left for current level")

def is_staff_equipped():
    """Check if staff of air is equipped using gear data."""
    gear_data = gear()
    if gear_data and 'data' in gear_data:
        for item in gear_data['data']:
            if isinstance(item, dict) and item.get('name', '').lower() == 'staff of air':
                print("Staff of air is equipped")
                return True
            elif isinstance(item, str) and 'staff of air' in item.lower():
                print("Staff of air is equipped (string match)")
                return True
    print("Staff of air is not equipped")
    return False

def equip_staff():
    """Equip the staff of air from inventory after opening inventory with F1."""
    keyboard.press_and_release("f1")
    print("Pressed F1 to open inventory")
    max_attempts = 30  # ~3s timeout
    for attempt in range(max_attempts):
        staff = inventory(item="staff of air", middle_point=True)
        if staff and 'data' in staff and staff['data']:
            staff_point = staff['data'][0].get('random_clickpoint')
            if staff_point:
                print(f"Clicking staff at {staff_point['x'] + rl_x}, {staff_point['y'] + rl_y} (random_clickpoint from plugin)")
                mouse(staff_point['x'] + rl_x, staff_point['y'] + rl_y, button="left", fast=True, sleep=True)
                print(f"Attempted to equip staff of air at x={staff_point['x'] + rl_x}, y={staff_point['y'] + rl_y}")
                # Poll until equipped
                equip_timeout = 20  # ~2s
                for _ in range(equip_timeout):
                    if is_staff_equipped():
                        print("Staff equipped successfully")
                        return True
                    time.sleep(0.1)
        print(f"Retrying to find/equip staff (attempt {attempt + 1})")
        time.sleep(0.1)
    print("Failed to equip staff of air after retries")
    return False

def open_spellbook():
    """Open the spellbook tab by pressing F4 and poll until open."""
    keyboard.press_and_release("f4")
    print("Pressed F4 to open spellbook tab")
    # Poll until spellbook is open
    open_timeout = 20  # ~2s
    for _ in range(open_timeout):
        widgets = get_all_widget_data()
        spellbook_open = any(widget.get("id") == 35913797 and widget.get("spriteId", -1) != -1 for widget in widgets)
        if spellbook_open:
            print("Spellbook opened successfully")
            return True
        time.sleep(0.1)
    print("Failed to open spellbook after polling")
    return False

def cast_varrock_teleport():
    """Check spellbook and Varrock Teleport availability, then cast the spell."""
    spellbook_id = 35913797
    varrock_teleport_id = 14286871
    max_attempts = 3  # Increased attempts for robustness
    attempt = 0

    while attempt < max_attempts:
        widgets = get_all_widget_data()
        if not widgets:
            print("No widget data received, retrying")
            time.sleep(0.5)
            attempt += 1
            continue

        spellbook_open = False
        varrock_available = False
        varrock_clickpoint = None

        for widget in widgets:
            if widget.get("id") == spellbook_id:
                sprite_id = widget.get("spriteId", -1)
                if sprite_id != -1:
                    spellbook_open = True
                    print(f"Spellbook widget: id={spellbook_id}, spriteId={sprite_id}")
            
            if widget.get("id") == varrock_teleport_id:
                sprite_id = widget.get("spriteId", -1)
                bounds = widget.get("bounds", {})
                print(f"Varrock Teleport widget: id={varrock_teleport_id}, spriteId={sprite_id}, bounds={bounds}")
                if sprite_id == 27:
                    varrock_available = True
                    # Relax bounds check: use fallback coordinates if bounds are invalid
                    if bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                        varrock_clickpoint = (
                            bounds["x"] + random.randint(bounds["width"]//4, 3*bounds["width"]//4),
                            bounds["y"] + random.randint(bounds["height"]//4, 3*bounds["height"]//4)
                        )
                        print(f"Varrock clickpoint calculated as {varrock_clickpoint} (random within inset bounds)")
                    else:
                        # Fallback coordinates based on typical Varrock Teleport position
                        varrock_clickpoint = (590, 268)  # From camera.py comment
                        print("Using fallback clickpoint for Varrock Teleport due to invalid bounds: (590, 268)")

        if spellbook_open and varrock_available and varrock_clickpoint:
            # Cast Varrock Teleport
            x, y = varrock_clickpoint
            print(f"Clicking Varrock Teleport at {x + rl_x}, {y + rl_y}")
            mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
            # Poll until in Varrock (x 3200-3220, y 3410-3440)
            teleport_timeout = 50  # ~5s
            for _ in range(teleport_timeout):
                player_data = player(location=True)
                loc = player_data.get('data', {}).get('location', {})
                px, py = loc.get('x', 0), loc.get('y', 0)
                if 3200 <= px <= 3220 and 3410 <= py <= 3440:
                    print("Teleported to Varrock successfully")
                    return True
                time.sleep(0.1)
            print("Teleport timed out")
            return False
        
        if not spellbook_open and attempt == 0:
            print("Spellbook is not open, attempting to open with F4")
            if not open_spellbook():
                print("Failed to open spellbook, cannot teleport")
                return False
        elif not varrock_available:
            print("Varrock Teleport not available (SpriteId != 27)")
            return False
        elif not varrock_clickpoint:
            print("Varrock Teleport available but no valid clickpoint")
            return False
        
        attempt += 1
        time.sleep(0.5)  # Wait before rechecking

    print("Failed to cast Varrock Teleport after attempts")
    return False

def start_bank():
    """Open bank and withdraw items; first time includes tinderbox and runes, later only logs."""
    global initial_items_withdrawn

    # Get current camera settings
    original_camera = player(camera=True).get('data', {}).get('camera', {})
    original_pitch = original_camera.get('pitch', 302)
    original_yaw = original_camera.get('yaw', 1862)
    original_zoom = original_camera.get('zoom', 349)

    bank_object = game_object("34810", tile_radius=50)
    print(bank_object)

    if not bank_object or 'data' not in bank_object or not bank_object['data']:
        print("No bank found initially, adjusting camera")
        camera(pitch=198, yaw=273, zoom=253)
        time.sleep(0.5)  # Brief wait for camera adjustment
        bank_object = game_object("34810", tile_radius=50)
        print(bank_object)
        if not bank_object or 'data' not in bank_object or not bank_object['data']:
            camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
            exit("No bank found even after camera adjustment")

    bank_data = bank_object['data'][0]
    middle_point = bank_data.get('middle_point')
    if middle_point:
        x, y = middle_point['x'], middle_point['y']
        # Check if bank is within visible screen range
        if not (0 <= x <= 512 and 0 <= y <= 334):
            print("Bank not within visible screen range, adjusting camera")
            camera(pitch=198, yaw=273, zoom=253)
            time.sleep(0.5)
            bank_object = game_object("34810", tile_radius=50)
            if not bank_object or 'data' not in bank_object or not bank_object['data']:
                camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
                exit("No bank found even after camera adjustment")
            bank_data = bank_object['data'][0]
            middle_point = bank_data.get('middle_point')
            if middle_point:
                x, y = middle_point['x'], middle_point['y']
            else:
                camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
                exit("No middle_point for bank after adjustment")

        # Hover over the bank to check default action
        print(f"Hovering over bank at {x + rl_x}, {y + rl_y} (middle_point from game_object)")
        mouse(x + rl_x, y + rl_y)  # Move mouse without clicking
        time.sleep(0.2)

        # Get interact options (potential menu)
        options = interact_options()
        if options and 'data' in options and options['data']:
            first_option = options['data'][0]['option'].lower()
            if first_option == 'bank':
                # Left-click directly
                print(f"Default action is 'Bank', left-clicking at {x + rl_x}, {y + rl_y}")
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
            else:
                # Right-click and select 'Bank'
                print(f"Default action is not 'Bank' ({first_option}), right-clicking")
                mouse(x + rl_x, y + rl_y, button="right", fast=True, sleep=True)
                time.sleep(0.2)
                options = interact_options()  # Now with open menu
                for option in options['data']:
                    if option['option'].lower() == 'bank':
                        menu_point = option.get('middle_point')
                        if menu_point:
                            menu_x, menu_y = menu_point['x'], menu_point['y']
                            print(f"Selecting 'Bank' from menu at {menu_x + rl_x}, {menu_y + rl_y} (middle_point from interact_options)")
                            mouse(menu_x + rl_x, menu_y + rl_y, button="left", fast=True, sleep=True)
                            break
                else:
                    print("No 'Bank' option found in menu")
                    camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
                    return False
        else:
            print("No interact options found after hovering")
            camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
            return False

        # Wait up to 10 seconds for bank to open
        for _ in range(100):
            bank_data = bank_items()
            print(f"bank_items response: {bank_data}")
            if bank_data and 'data' in bank_data and bank_data['data'] is not None and len(bank_data['data']) > 0:
                print("Bank interface opened")
                success = False
                if not initial_items_withdrawn:
                    # First time: withdraw tinderbox, law runes, fire runes, staff of air
                    if bank(withdraw="tinderbox", deposit_inventory=True, deposit_equipment=True, placeholder=True, quantity="1", noted=False):
                        # Check for law runes, fire runes, staff of air; exit if any are missing
                        if not bank(withdraw="law rune", placeholder=True, quantity="all", noted=False):
                            exit("No law runes found, exiting")
                        print("Withdrew all law runes")
                        if not bank(withdraw="fire rune", placeholder=True, quantity="all", noted=False):
                            exit("No fire runes found, exiting")
                        print("Withdrew all fire runes")
                        if not bank(withdraw="staff of air", placeholder=True, quantity="1", noted=False):
                            exit("No staff of air found, exiting")
                        print("Withdrew staff of air")
                        if withdraw_logs():  # Withdraw logs
                            success = True
                            initial_items_withdrawn = True  # Mark initial items as withdrawn
                else:
                    # Subsequent times: only withdraw logs
                    if withdraw_logs():
                        success = True

                # Check if bank is still open
                bank_data_check = bank_items()
                print(f"bank_items post-quantity response: {bank_data_check}")
                if bank_data_check and 'data' in bank_data_check and bank_data_check['data'] is not None and len(bank_data_check['data']) > 0:
                    print("Bank interface still open after quantity action, pressing Escape")
                    keyboard.press_and_release("esc")
                    time.sleep(0.5)  # Increased delay

                # Restore original camera after banking
                camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)

                if success:
                    return True
                else:
                    return False
            time.sleep(0.1)
        exit("Bank failed to open after 10 seconds")
    else:
        print("No bank found even after camera adjustment")
        # Restore camera
        camera(pitch=original_pitch, yaw=original_yaw, zoom=original_zoom)
        exit()

def walk_to_tile(tile_x: int, tile_y: int, max_attempts: int = 5):
    """Walk to a specific tile by clicking its screen position, ensuring 'Walk here' option, retrying if needed."""
    for attempt in range(max_attempts):
        tile_data = tile(tile_x, tile_y, tile_radius=20, middle_point=True)
        if tile_data and 'data' in tile_data and tile_data['data']:
            for t in tile_data['data']:
                if t.get('x') == tile_x and t.get('y') == tile_y:
                    tile_point = t.get('middle_point')
                    if tile_point:
                        # Hover to check options
                        hover_x, hover_y = tile_point['x'], tile_point['y']
                        mouse(hover_x + rl_x, hover_y + rl_y)  # Hover
                        time.sleep(0.2)
                        options = interact_options().get('data', [])
                        is_walk_left_click = options and options[0]['option'].lower() == 'walk here'

                        if is_walk_left_click:
                            # Left-click directly
                            print(f"Default action is 'Walk here', left-clicking at {hover_x + rl_x}, {hover_y + rl_y}")
                            mouse(hover_x + rl_x, hover_y + rl_y, button="left", fast=True, sleep=True)
                        else:
                            # Right-click and select 'Walk here'
                            print("Default action is not 'Walk here', right-clicking")
                            mouse(hover_x + rl_x, hover_y + rl_y, button="right", fast=True, sleep=True)
                            time.sleep(0.2)
                            options = interact_options().get('data', [])  # Refresh with menu open
                            for option in options:
                                if option['option'].lower() == 'walk here':
                                    menu_point = option.get('middle_point')
                                    if menu_point:
                                        menu_x, menu_y = menu_point['x'], menu_point['y']
                                        print(f"Selecting 'Walk here' from menu at {menu_x + rl_x}, {menu_y + rl_y}")
                                        mouse(menu_x + rl_x, menu_y + rl_y, button="left", fast=True, sleep=True)
                                        break
                            else:
                                print("No 'Walk here' option found in menu")
                                continue

                        # Poll until arrived
                        walk_timeout = 50  # ~5s
                        for _ in range(walk_timeout):
                            player_data = player(location=True)
                            current_tile = player_data.get('data', {}).get('location', {})
                            current_x = current_tile.get('x', 0)
                            current_y = current_tile.get('y', 0)
                            if current_x == tile_x and current_y == tile_y:
                                print(f"Arrived at tile ({tile_x}, {tile_y})")
                                return True
                            time.sleep(0.1)
                        print(f"Walk timed out (attempt {attempt + 1})")
                    else:
                        print(f"No middle_point for tile ({tile_x}, {tile_y})")
                    break  # Stop searching once the target tile is found
            else:
                print(f"Target tile ({tile_x}, {tile_y}) not found in data")
        else:
            print(f"Failed to find tile data for ({tile_x}, {tile_y})")
        time.sleep(0.5)  # Delay before retry
    print(f"Failed to reach tile ({tile_x}, {tile_y}) after {max_attempts} attempts")
    return False

def move_to_clear_tile():
    """Find and walk to a nearby walkable tile without a fire on it, ensuring 'Walk here' option."""
    player_data = player(location=True)
    current_tile = player_data.get('data', {}).get('location', {})
    current_x = current_tile.get('x', 0)
    current_y = current_tile.get('y', 0)
    
    walkable_data = walkable_tile(current_x, current_y, tile_radius=2, middle_point=True)
    if walkable_data and 'data' in walkable_data:
        candidate_tiles = []
        for wt in walkable_data['data']:
            wt_x = wt.get('x')
            wt_y = wt.get('y')
            # Check if this tile has a fire
            fires = game_object("fire", tile_radius=0)
            has_fire = False
            if fires and 'data' in fires:
                for fire in fires['data']:
                    if fire.get('x') == wt_x and fire.get('y') == wt_y:
                        has_fire = True
                        break
            if not has_fire:
                candidate_tiles.append(wt)
        
        if candidate_tiles:
            # Pick a random candidate
            target_tile = random.choice(candidate_tiles)
            target_x = target_tile.get('x')
            target_y = target_tile.get('y')
            middle_point = target_tile.get('middle_point')
            if middle_point:
                # Hover to check options
                hover_x, hover_y = middle_point['x'], middle_point['y']
                mouse(hover_x + rl_x, hover_y + rl_y)  # Hover
                time.sleep(0.2)
                options = interact_options().get('data', [])
                is_walk_left_click = options and options[0]['option'].lower() == 'walk here'

                if is_walk_left_click:
                    # Left-click directly
                    print(f"Default action is 'Walk here', left-clicking at {hover_x + rl_x}, {hover_y + rl_y}")
                    mouse(hover_x + rl_x, hover_y + rl_y, button="left", fast=True, sleep=True)
                else:
                    # Right-click and select 'Walk here'
                    print("Default action is not 'Walk here', right-clicking")
                    mouse(hover_x + rl_x, hover_y + rl_y, button="right", fast=True, sleep=True)
                    time.sleep(0.2)
                    options = interact_options().get('data', [])  # Refresh with menu open
                    for option in options:
                        if option['option'].lower() == 'walk here':
                            menu_point = option.get('middle_point')
                            if menu_point:
                                menu_x, menu_y = menu_point['x'], menu_point['y']
                                print(f"Selecting 'Walk here' from menu at {menu_x + rl_x}, {menu_y + rl_y}")
                                mouse(menu_x + rl_x, menu_y + rl_y, button="left", fast=True, sleep=True)
                                break
                    else:
                        print("No 'Walk here' option found in menu")
                        return False

                # Poll until arrived
                move_timeout = 20  # ~2s
                for _ in range(move_timeout):
                    player_data = player(location=True)
                    loc = player_data.get('data', {}).get('location', {})
                    if loc.get('x') == target_x and loc.get('y') == target_y:
                        print("Moved to clear tile successfully")
                        return True
                    time.sleep(0.1)
                print("Move to clear tile timed out")
                return False
        else:
            print("No clear walkable tiles nearby")
    return False

def is_inventory_open():
    """Check if inventory tab is open using widget ID 35913802."""
    widgets = get_all_widget_data()
    if widgets:
        for widget in widgets:
            if widget.get("id") == 35913802:
                sprite_id = widget.get("spriteId", -1)
                print(f"Inventory widget spriteId: {sprite_id}")
                return sprite_id != -1
    return False

def has_fire_on_tile():
    """Check if there is a fire object on the player's current tile."""
    player_data = player(location=True)
    current_tile = player_data.get('data', {}).get('location', {})
    current_x = current_tile.get('x', 0)
    current_y = current_tile.get('y', 0)
    
    fires = game_object("fire", tile_radius=0)
    if fires and 'data' in fires and fires['data']:
        print("Fire detected on current tile")
        return True
    return False

def logout_and_break(break_minutes):
    """Logout, take a break for specified minutes, and log back in. Prints timestamps and duration."""
    print("Initiating logout for break")
    # Logout clicks
    mouse(651 + rl_x, 485 + rl_y, button="left", fast=True, sleep=True)
    time.sleep(random.uniform(0.22, 0.25))
    mouse(651 + rl_x, 433 + rl_y, button="left", fast=True, sleep=True)
    
    # Poll until at LOGIN_SCREEN
    logout_timeout = 20  # ~2s
    for _ in range(logout_timeout):
        if game_state().get('data') == "LOGIN_SCREEN":
            print("Logged out successfully")
            break
        time.sleep(0.1)
    else:
        print("Logout timed out")
        return

    # Calculate and print times
    break_seconds = break_minutes * 60
    start_time = datetime.now()
    resume_time = start_time + timedelta(seconds=break_seconds)
    duration = timedelta(seconds=break_seconds)
    print(f"Break started at: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Script will resume at: {resume_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Sleep duration: {str(duration).split('.')[0]}")  # hh:mm:ss format

    time.sleep(break_seconds)

    # Log back in
    mouse(391 + rl_x, 265 + rl_y, button="left", fast=True, sleep=True)
    # Poll for login states, up to 15 seconds total
    start_time_poll = time.time()
    first_logged_in = False
    while time.time() - start_time_poll < 15:
        state = game_state().get('data')
        print(f"Main Menu Data: {{'data': '{state}'}}")
        if state == 'LOGGED_IN' and not first_logged_in:
            time.sleep(0.4)  # Wait 0.4s before click
            mouse(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
            time.sleep(0.6)  # Wait 0.6s after click
            print("Clicked post-login button after first LOGGED_IN")
            first_logged_in = True
            return True  # Exit early after successful login and clicks
        time.sleep(0.1)
    print("Login timed out after 15 seconds")
    exit("Failed to log back in")

def perform_firemaking():
    """Use tinderbox on logs to light fires, checking XP and inventory count."""
    if not is_inventory_open():
        keyboard.press_and_release("f1")
        print("Pressed F1 to open inventory for firemaking")
        time.sleep(1.0)  # Increased delay for inventory to load
    
    while True:
        logs = inventory(item="logs", middle_point=True)
        if not logs or not 'data' in logs or not logs['data']:
            logs = inventory(item="oak logs", middle_point=True)
            if not logs or not 'data' in logs or not logs['data']:
                logs = inventory(item="willow logs", middle_point=True)
                if not logs or not 'data' in logs or not logs['data']:
                    logs = inventory(item="maple logs", middle_point=True)
                    if not logs or not 'data' in logs or not logs['data']:
                        print("No logs left in inventory")
                        print(inventory(item="logs"))  # Debug print
                        return True  # Done with firemaking for this batch
        # Use the found logs
        initial_logs_count = len(logs['data'])
        firemaking_stats = plugin_stats().get('data', {}).get('Firemaking', {})
        initial_xp = firemaking_stats.get('xp', 0)
        print(f"Initial logs count: {initial_logs_count}, Initial Firemaking XP: {initial_xp}")

        tinderbox = inventory(item="tinderbox", middle_point=True)
        if tinderbox and 'data' in tinderbox and tinderbox['data']:
            tinderbox_point = tinderbox['data'][0].get('random_clickpoint')
            logs_point = logs['data'][0].get('random_clickpoint')
            if tinderbox_point and logs_point:
                if has_fire_on_tile():
                    print("Fire detected on current tile, moving to clear tile...")
                    if not move_to_clear_tile():
                        print("Failed to move to clear tile, waiting instead...")
                        time.sleep(1)  # Fallback wait
                    continue

                print(f"Clicking tinderbox at {tinderbox_point['x'] + rl_x}, {tinderbox_point['y'] + rl_y} (random_clickpoint from inventory)")
                mouse(tinderbox_point['x'] + rl_x, tinderbox_point['y'] + rl_y, button="left", fast=True, sleep=True)
                time.sleep(0.1)
                print(f"Clicking log at {logs_point['x'] + rl_x}, {logs_point['y'] + rl_y} (random_clickpoint from inventory)")
                mouse(logs_point['x'] + rl_x, logs_point['y'] + rl_y, button="left", fast=True, sleep=True)
                time.sleep(0.5)  # Initial wait for action to start

                # Check if log was used and XP increased
                max_check_attempts = 100  # Up to ~30 seconds (0.3s * 100)
                for _ in range(max_check_attempts):
                    current_logs = inventory(item="logs", middle_point=True)
                    if not current_logs or not 'data' in current_logs or not current_logs['data']:
                        current_logs = inventory(item="oak logs", middle_point=True)
                        if not current_logs or not 'data' in current_logs or not current_logs['data']:
                            current_logs = inventory(item="willow logs", middle_point=True)
                            if not current_logs or not 'data' in current_logs or not current_logs['data']:
                                current_logs = inventory(item="maple logs", middle_point=True)
                    current_logs_count = len(current_logs['data']) if current_logs and 'data' in current_logs else 0
                    current_stats = plugin_stats().get('data', {}).get('Firemaking', {})
                    current_xp = current_stats.get('xp', 0)

                    if current_logs_count == initial_logs_count - 1 and current_xp > initial_xp:
                        print(f"Log ignited successfully. Logs count: {current_logs_count}, New XP: {current_xp}")
                        # 0.1% chance for long break after each log burned
                        if random.random() < 0.001:
                            logout_and_break(random.uniform(30, 90))  # 30-90 minutes
                        # 1% chance for short break
                        elif random.random() < 0.01:
                            short_sleep = random.uniform(15, 180)
                            print(f'sleeping for {short_sleep}')
                            time.sleep(short_sleep) # sleep for 15seconds - 3 minutes
                        else:
                            time.sleep(0.1)  # Short wait before next log
                        break
                    time.sleep(0.3)  # Check every 0.3 seconds
                
                else:
                    print("Failed to ignite log after checks")
                    return False
            else:
                print("Failed to find clickpoints for tinderbox or log")
                return False
        else:
            print("Failed to find tinderbox in inventory")
            return False

def firemaking():
    """Main firemaking loop: bank for items, equip staff if needed, teleport, walk to alternating tile, then perform firemaking."""
    global initial_items_withdrawn, use_first_tile
    print(f"Starting firemaking: initial_items_withdrawn={initial_items_withdrawn}")
    camera(pitch=302, yaw=1862, zoom=349)
    if game_state().get('data') != "LOGGED_IN":
        print("Not logged in, exiting")
        exit()
    while True:
        if start_bank():
            print("Banking complete")
            time.sleep(0.5)  # Additional delay to ensure inventory updates
            
            # Check and equip staff if not equipped
            if not is_staff_equipped():
                if equip_staff():
                    print("Staff equipped")
                else:
                    print("Failed to equip staff, exiting")
                    exit()
            else:
                print("Staff already equipped, skipping equip")
            
            # Always teleport after banking
            if cast_varrock_teleport():
                print("Teleported to Varrock")
                
                # Alternate tiles
                target_tile_y = 3429 if use_first_tile else 3428
                use_first_tile = not use_first_tile  # Toggle for next time
                if walk_to_tile(3209, target_tile_y):
                    print(f"Walked to tile (3209, {target_tile_y})")
                else:
                    print(f"Failed to walk to tile (3209, {target_tile_y}), continuing anyway")
            else:
                print("Failed to teleport to Varrock, exiting")
                exit()
            
            print("Proceeding to firemaking")
            if not perform_firemaking():
                print("Failed to perform firemaking")
                break
        else:
            print("Banking failed")
            break

rl_x, rl_y = runelite_window(0, 0)
# time.sleep(1)
# firemaking()