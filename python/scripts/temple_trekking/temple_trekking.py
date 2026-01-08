
from modules.utils.wait_for_tick import wait_for_tick
import time, re, random, math, keyboard
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.inventory import check_inventory, get_inventory_count, click_inventory_sequence
from modules.widgets.widget import check_widget_text, click_widget, check_widget_name, check_widget, get_widget, click_widget_child
from modules.core.plugin_client import tile, stats
from modules.weapon_data.combat_style import combat_style
from modules.utils.camera import camera
from modules.utils.select_menu_option import select_menu_option
from modules.player_data.click_equipment import click_equipment_item
from modules.utils.inventory import click_inventory
from modules.object_data.game_object import click_gameobject, get_closest_game_object, get_game_objects, hover_gameobject
from modules.core.plugin_client import fetch_object
from modules.object_data.object import click_object, check_object, get_closest_object, use_on_object
from modules.core.mouse_control import move, get_cursor_pos
from modules.widgets.widget_data import get_all_widget_data
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_npc, click_closest_npc

# Additional imports for ground item handling
from modules.core.plugin_client import inventory, interact_options


def check_inventory(item: str, click: bool = False, clicks: int = 1) -> bool:
    """
    Check if the inventory is open and contains the specified item.
    Opens the inventory with F1 if closed, counts the item, and prints its quantity.
    Optionally clicks on the first instance of the item.
    Returns True if the item is found, False if none are found and inventory is open.
    """
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Get current inventory data
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data. Attempting to open inventory...")
        keyboard.press_and_release("f1")
        print("Pressed F1 to open inventory.")
        time.sleep(0.05)  # Wait for inventory to open
        
        # Retry inventory check up to 3 times
        for _ in range(3):
            inv_data = inventory()
            if inv_data and 'data' in inv_data and inv_data['data']:
                break
            time.sleep(0.1)
        else:
            print("Inventory still inaccessible after opening attempts.")
            return False

    # Extract item names
    items = [inv_item.get('name', '').strip().lower() for inv_item in inv_data['data'] if 'name' in inv_item]
    target_item = item.lower().strip()
    count = sum(1 for i in items if i == target_item)

    # Format and print found item count
    if count > 0:
        print(f"{item} x{count}")
        
        # Optionally click on the first instance
        if click and inv_data['data']:
            first_item = next((inv_item for inv_item in inv_data['data'] if inv_item.get('name', '').strip().lower() == target_item), None)
            if first_item and 'middle_point' in first_item:
                bounds = first_item['middle_point']
                canvas_x = bounds['x']
                canvas_y = bounds['y']
                screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                for _ in range(clicks):
                    move(screen_x, screen_y, button='left', fast=True, sleep=True)
                    print(f"Clicked on {item}")
                    if clicks > 1:
                        wait_for_tick(ticks=2)
        return True
    else:
        print(f"No {item} found in inventory.")
        return False

def use_tome():
    # Focus RuneLite window
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return
    
    ensure_inventory_open()

    # Check if inventory is open and click 'reward token'
    if not check_inventory('reward token', click=True, clicks=1):
        print("Failed to find or click 'reward token'.")
        return

    # Loop until widget 17956870 is clicked
    wait_for_tick(ticks=2)
    while not click_widget_child('17956870', child_index=7):
        wait_for_tick(ticks=1)  # Wait 1 tick before retry

    # Loop until widget 17956876 is clicked
    while not click_widget('17956875'):
        wait_for_tick(ticks=1)  # Wait 1 tick before retry

    # Wait for 1 tick
    wait_for_tick(ticks=2)

    # List of tomes to check and click if found
    tomes = [
        'firemaking tome',
        'agility tome',
        'fishing tome',
        'mining tome',
        'slayer tome',
        'thieving tome',
        'woodcutting tome'
    ]

    # Check for any tome in inventory and click the first one found
    for tome in tomes:
        if check_inventory(tome, click=True, clicks=1):
            print(f"Clicked on {tome}.")
            for _ in range(2):
                for _ in range(random.randint(2, 4)):
                    keyboard.press('space')
                    time.sleep(random.uniform(0.04, 0.08))
                    keyboard.release('space')
                wait_for_tick(ticks=1)

            return True
    else:
        print("No matching tomes found in inventory.")


def wait_for_item_in_inventory(item_name: str, initial_quantity: int = 0):
    """
    Wait until the item appears in the inventory or quantity increases for stackable items.
    """
    max_wait_ticks = 2  # Reduced to 2 ticks (~1.2s max)
    current_tick = gametick().get('data', 0)
    end_tick = current_tick + max_wait_ticks
    item_name_lower = item_name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()  # Ignore doses

    while gametick().get('data', 0) < end_tick:
        inv_data = inventory(item=item_name)
        if inv_data and 'data' in inv_data:
            for inv_item in inv_data['data']:
                inv_item_name_lower = inv_item.get('item', '').lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()
                if inv_item_name_lower == item_name_lower:
                    inv_quantity = inv_item.get('quantity', 0)
                    if inv_quantity > initial_quantity:
                        print(f"Item {item_name} detected in inventory with quantity {inv_quantity}.")
                        return True
        time.sleep(0.05)  # Fast polling
    print(f"Timeout waiting for {item_name} in inventory. Assuming success and proceeding.")
    return True  # Assume success on timeout to avoid blocking


def clean_target_name(target: str) -> str:
    """
    Remove color tags (e.g., <col=ff9040>) and quantity suffixes from the target name.
    """
    if target.startswith('<col='):
        end_idx = target.find('>')
        if end_idx != -1:
            target = target[end_idx + 1:]
    # Remove ' x N' suffixes
    if ' x ' in target:
        target = target.split(' x ')[0]
    return target.strip()


def point_in_polygon(x, y, polygon):
    """
    Ray-casting algorithm to check if point (x,y) is inside polygon.
    """
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside


def is_in_temple_trekking_area():
    """
    Check if the player is inside one of the two Temple Trekking starting areas (on plane 0).
    Returns True if in Burgh de Rott or Canifis gate area.
    """
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data:
        print("Failed to fetch player data for area check.")
        return False
    
    loc = pl_data['data']['location']
    px, py, pz = loc['x'], loc['y'], loc['plane']
    
    if pz != 0:
        return False
    
    burgh_de_rott_area = [
        (3475, 3241), (3481, 3246), (3489, 3245), (3493, 3234),
        (3485, 3229), (3471, 3230), (3475, 3241)
    ]
    canifis_area = [
        (3428, 3492), (3440, 3491), (3441, 3475), (3432, 3475),
        (3422, 3485), (3428, 3492)
    ]
    
    in_area1 = point_in_polygon(px, py, burgh_de_rott_area)
    in_area2 = point_in_polygon(px, py, canifis_area)
    
    if in_area1 or in_area2:
        print(f"Player at ({px}, {py}) is in Temple Trekking starting area.")
        for _ in range(2):
            for _ in range(random.randint(2, 4)):
                keyboard.press('space')
                time.sleep(random.uniform(0.04, 0.08))
                keyboard.release('space')
            wait_for_tick(1)

    
    return in_area1 or in_area2


def is_inventory_open():
    """Check if the inventory tab is open (spriteId 1030 on widget 35913795)."""
    widgets = get_all_widget_data()
    if widgets:
        for widget in widgets:
            widget_id = widget.get('id', 0) or widget.get('packedId', 0)
            if widget_id == 35913795:  # Correct widget ID
                sprite_id = widget.get('spriteId', -1)
                return sprite_id == 1030
    return False


def ensure_inventory_open(max_attempts=3):
    """Ensure inventory is open by pressing F1 if needed."""
    focus_runelite_window()
    for attempt in range(1, max_attempts + 1):
        if is_inventory_open():
            return True
        print(f"Inventory not open (attempt {attempt}), pressing F1")
        keyboard.press_and_release("f1")
        time.sleep(0.5)
    print("Failed to open inventory after attempts.")
    return False


def ensure_camera_settings(pitch=491, yaw=0, zoom=192, tolerance=(50, 50, 50)):
    """Set camera to target values if outside tolerance."""
    camera_data = player(camera=True).get('data', {}).get('camera', {})
    current_pitch = camera_data.get('pitch', 0)
    current_yaw = camera_data.get('yaw', 0)
    current_zoom = camera_data.get('zoom', 0)
    
    pitch_tol, yaw_tol, zoom_tol = tolerance
    if (abs(current_pitch - pitch) <= pitch_tol and
        abs(current_yaw - yaw) <= yaw_tol and
        abs(current_zoom - zoom) <= zoom_tol):
        return True
    
    print(f"Adjusting camera to pitch={pitch}, yaw={yaw}, zoom={zoom}")
    camera(pitch=pitch, yaw=yaw, zoom=zoom)
    return True


def evade_event():
    """Evade event only if the 'Evade-event' object is actually present."""
    print("Checking for Evade-event option...")
    evade_obj = get_closest_object('13831', 'Evade-event')
    if not evade_obj:
        print("No 'Evade-event' object found nearby – skipping evade.")
        return False
    
    print("Evading current event...")
    clicked = click_object('13831', 'Evade-event')
    if not clicked:
        print("Failed to click Evade-event object.")
        return False
    
    timeout_ticks = 15
    movement_started = False
    for _ in range(timeout_ticks):
        wait_for_tick(1)
        anim_data = player(animation=True)
        anim = anim_data.get('data', {}).get('animation', -1) if anim_data else -1
        if anim in {821, 822, 823, 824}:  # Walking/running animations
            movement_started = True
            break
    
    if movement_started:
        print("Character started moving after evade.")
        wait_for_tile_change()
        wait_for_tick(2)
        print("Event evaded successfully.")
        return True
    else:
        print("Timeout: No movement detected after evade click.")
        return False


def swamp_tree_room():
    def continue_trek():
        click_object('13832', 'continue-trek')
        wait_till_character_stopped_moving()
        return True

    def handle_swamp_tree_branch():
        pl_data = player(location=True)
        initial_loc = pl_data['data']['location']
        initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
        click_gameobject('13846', 'swing-from')
        for _ in range(10):
            wait_for_tick()
            pl_data = player(location=True)
            current_loc = pl_data['data']['location']
            current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
            if current_tile[1] > initial_tile[1] + 4:
                wait_for_tick(10)
                return True
        
    def use_long_vine_on_swamp_tree_branch():
        click_inventory('long vine', 'use')
        click_gameobject('13845', 'Use Long vine -> Swamp tree branch')
        while True:
            swamp_tree_branch = get_closest_game_object('13846', None, 10)
            if swamp_tree_branch:
                return True

    def cut_short_vines():
        vine_ids = ['13847', '13848', '13849']
        ensure_inventory_open()
        while get_inventory_count('short vine') < 3:
            increased = False
            for vine_id in vine_ids:
                old_count = get_inventory_count('short vine')
                if click_gameobject(vine_id, 'Cut-vine'):
                    for _ in range(40):
                        time.sleep(0.1)
                        if get_inventory_count('short vine') > old_count:
                            increased = True
                            break
                if increased:
                    break
            if not increased:
                print("No vines could be cut.")
                break
        click_inventory_sequence(['short vine', 'short vine'])
        wait_for_tick(5)
        return True

    swamp_tree_branch = get_closest_game_object('13846', None, 10)
    if swamp_tree_branch:
        if handle_swamp_tree_branch():
            if continue_trek():
                return True
        
    if get_inventory_count('long vine') > 0:
        if use_long_vine_on_swamp_tree_branch():
            if handle_swamp_tree_branch():
                if continue_trek():
                    return True

    if cut_short_vines():
        if get_inventory_count('long vine') > 0:
            if use_long_vine_on_swamp_tree_branch():
                if handle_swamp_tree_branch():
                    if continue_trek():
                        return True


def zombie_room():
    ensure_inventory_open()
    ensure_camera_settings(pitch=491, yaw=0, zoom=268)

    def go_to_broken_bridge():
        bridge = get_closest_object('13834', 'Inspect')
        if not bridge:
            return None
        target_tile = (bridge['tile']['x'], bridge['tile']['y'] - 1, bridge['tile']['plane'])
        curr = player(location=True).get('data', {}).get('location', {})
        if (curr.get('x'), curr.get('y'), curr.get('plane')) != target_tile:
            click_minimap_tile(*target_tile, target_zoom=5)
            wait_till_character_stopped_moving()
            wait_for_tick(3)
        return target_tile

    def get_ground_planks(radius=30):
        pl = player(location=True).get('data', {}).get('location', {})
        px, py = pl.get('x', 0), pl.get('y', 0)
        data = pick(px, py, size=radius, item='plank')
        if data and 'data' in data and 'items' in data['data']:
            items = data['data']['items']
            return len(items), items
        return 0, []

    def attack_next_lumberjack():
        return click_closest_npc('undead lumberjack', 'attack')

    def wait_for_plank_drop(prev_count):
        for _ in range(60):
            wait_for_tick(1)
            count, _ = get_ground_planks()
            if count > prev_count:
                print(f"Plank dropped! ({prev_count} -> {count})")
                return True, count
        print("No plank drop detected.")
        return False, prev_count

    def simple_pickup_plank(plank_item):
        if 'middle_point' not in plank_item:
            return False
        mp = plank_item['middle_point']
        rl_x, rl_y = runelite_window(mp['x'], mp['y'])
        move(rl_x, rl_y, fast=True, sleep=True)
        time.sleep(random.uniform(0.05, 0.15))

        menu = interact_options().get('data', [])
        is_take_top = False
        if menu:
            top = menu[0]
            opt = top.get('option', '').lower()
            tgt = clean_target_name(top.get('target', '')).lower()
            if opt.startswith('take') and 'plank' in tgt:
                is_take_top = True

        if is_take_top:
            move(button='left', fast=True, sleep=True)
        else:
            move(button='right', fast=True, sleep=False)
            time.sleep(0.1)
            menu = interact_options().get('data', [])
            take_entry = None
            for e in menu:
                if e.get('option', '').lower().startswith('take') and 'plank' in clean_target_name(e.get('target', '')).lower():
                    take_entry = e
                    break
            if take_entry and 'middle_point' in take_entry:
                emp = take_entry['middle_point']
                ex, ey = runelite_window(emp['x'], emp['y'])
                move(ex + random.randint(-8, 8), ey + random.randint(-3, 3), button='left', fast=True, sleep=True)
            else:
                move(get_cursor_pos()[0] + random.randint(150, 250), get_cursor_pos()[1], fast=False)
                return False

        initial = get_inventory_count('plank')
        return wait_for_item_in_inventory('plank', initial)

    def pickup_all_planks(target_count=3):
        picked = 0
        while picked < target_count:
            count, planks = get_ground_planks(radius=50)
            if count == 0:
                print("No more planks on ground.")
                break
            
            print(f"{count} plank(s) remaining on ground – picking next...")
            success = simple_pickup_plank(planks[0])  # Pick closest (assume sorted by pick())
            if success:
                picked += 1
                print(f"Plank picked ({picked}/{target_count}).")
            else:
                print("Failed to pick plank – retrying next fetch.")
            
            wait_for_tick(3)  # Delay before refetch

    # === MAIN ZOMBIE LOGIC ===
    target_tile = go_to_broken_bridge()
    if not target_tile:
        return

    ground_planks = 0
    lumberjack_was_absent = True  # Initial assume absent to wait on first spawn
    while ground_planks < 3:
        # Check if lumberjack is present
        lumberjack_data = npc(name='undead lumberjack')
        has_lumberjack = lumberjack_data and 'data' in lumberjack_data and lumberjack_data['data']

        if has_lumberjack:
            wait_for_tick(5)

            if not attack_next_lumberjack():
                wait_for_tick(5)
                continue
            success, ground_planks = wait_for_plank_drop(ground_planks)
            if not success:
                wait_for_tick(5)
            else:
                wait_for_tick(5)
        else:
            lumberjack_was_absent = True
            print("No lumberjack present – waiting 1 tick...")
            wait_for_tick(1)

    # Pickup phase – dynamically refetch after each attempt
    pickup_all_planks(target_count=3)

    # Return to spot
    curr = player(location=True).get('data', {}).get('location', {})
    if (curr.get('x'), curr.get('y'), curr.get('plane')) != target_tile:
        click_minimap_tile(*target_tile, target_zoom=5)
        wait_till_character_stopped_moving()
        wait_for_tick(3)

    # Use planks on bridge (adapted from dead_tree_room)
    def use_planks_on_broken_bridge():
        states = [
            (13834, 'Inspect', 'use plank -> broken bridge', 22533),
            (22533, 'Inspect', 'use plank -> Partially broken bridge', 22534),
            (22534, 'Inspect', 'use plank -> Slightly broken bridge', 22535),
        ]
        fixed_id = 22535
        cross_action = 'Cross'

        current_state_id = None
        for state_id, _, _, _ in states + [(fixed_id, None, None, None)]:
            if get_closest_object(str(state_id), 'Inspect' if state_id != fixed_id else cross_action):
                current_state_id = state_id
                break

        if current_state_id == fixed_id:
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True

        for state_id, repair_action, use_option, next_id in states:
            if current_state_id != state_id:
                continue
            click_inventory('plank', 'use')
            use_on_object(str(state_id), repair_action, use_option)
            while not get_closest_object(str(next_id), 'Inspect' if next_id != fixed_id else cross_action):
                wait_for_tick()
            current_state_id = next_id
            if current_state_id == fixed_id:
                break

        if get_closest_object(str(fixed_id), cross_action):
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True
        return False

    # Use planks only if we have at least 3 in inventory
    if get_inventory_count('plank') >= 3:
        print("Using planks on broken bridge...")
        use_planks_on_broken_bridge()
    else:
        print("Not enough planks – skipping bridge repair.")

    def continue_trek():
        if click_object('13832', 'continue-trek'):
            wait_till_character_stopped_moving()
            return True

    if continue_trek():
        print("Zombie room completed.")


def dead_tree_room():
    ensure_inventory_open()
    
    def continue_trek():
        click_object('13832', 'continue-trek')
        return True

    def use_logs_on_broken_bridge():
        states = [
            (13834, 'Inspect', 'use logs -> broken bridge', 13835),
            (13835, 'Inspect', 'use logs -> Partially broken bridge', 13836),
            (13836, 'Inspect', 'use logs -> Slightly broken bridge', 13837),
        ]
        fixed_id = 13837
        cross_action = 'Cross'

        current_state_id = None
        for state_id, _, _, _ in states + [(fixed_id, None, None, None)]:
            if get_closest_object(str(state_id), 'Inspect' if state_id != fixed_id else cross_action):
                current_state_id = state_id
                break

        if current_state_id == fixed_id:
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True

        for state_id, repair_action, use_option, next_id in states:
            if current_state_id != state_id:
                continue
            click_inventory('logs', 'use')
            use_on_object(str(state_id), repair_action, use_option)
            while not get_closest_object(str(next_id), 'Inspect' if next_id != fixed_id else cross_action):
                wait_for_tick()
            current_state_id = next_id
            if current_state_id == fixed_id:
                break

        if get_closest_object(str(fixed_id), cross_action):
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True
        return False

    def go_to_broken_bridge():
        bridge = get_closest_object('13834', 'Inspect')
        if bridge:
            bridge_tile = bridge['tile']
            target_tile = (bridge_tile['x'], bridge_tile['y'] - 1, bridge_tile['plane'])
            click_minimap_tile(*target_tile, target_zoom=5)
            wait_till_character_stopped_moving()
            return True

    def cut_dead_trees(target_logs=3):
        current_logs = get_inventory_count('logs')
        if current_logs >= target_logs:
            return True
        while current_logs < target_logs:
            progress = False
            for _ in range(3):
                if click_gameobject('1365', 'chop down'):
                    for _ in range(30):
                        wait_for_tick()
                        new_logs = get_inventory_count('logs')
                        if new_logs > current_logs:
                            current_logs = new_logs
                            progress = True
                            break
                if progress:
                    break
            if not progress:
                break
        return True

    if cut_dead_trees():
        if go_to_broken_bridge():
            if use_logs_on_broken_bridge():
                continue_trek()
                return True


def start_temple_trekking():
    option = 'Escort'
    max_attempts = 5

    # Determine which starting area we are in to select correct NPCs
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data:
        print("Failed to fetch player location for NPC selection.")
        return False
    
    loc = pl_data['data']['location']
    px, py, pz = loc['x'], loc['y'], loc['plane']
    
    if pz != 0:
        print("Player not on ground plane.")
        return False
    
    burgh_de_rott_area = [
        (3475, 3241), (3481, 3246), (3489, 3245), (3493, 3234),
        (3485, 3229), (3471, 3230), (3475, 3241)
    ]
    canifis_area = [
        (3428, 3492), (3440, 3491), (3441, 3475), (3432, 3475),
        (3422, 3485), (3428, 3492)
    ]
    
    if point_in_polygon(px, py, burgh_de_rott_area):
        escort_ids = [1566, 1567]
        print("Detected Burgh de Rott starting area – targeting NPCs 1566 and 1567.")
    elif point_in_polygon(px, py, canifis_area):
        escort_ids = [1577, 1578]
        print("Detected Canifis/Paterdomus starting area – targeting NPCs 1577 and 1578.")
    else:
        print("Player not in a recognized Temple Trekking starting area.")
        return False

    for attempt in range(1, max_attempts + 1):
        print(f"Start Temple Trekking attempt {attempt}/{max_attempts}")
        
        ensure_camera_settings(pitch=491, yaw=0, zoom=192)
        
        success = click_closest_npc(escort_ids, option)
        if not success:
            print(f"Attempt {attempt}: NPC click failed.")
            if attempt < max_attempts:
                wait_for_tick(2)
            continue
        
        print("Waiting for Temple Trekking interface...")
        interface_found = False
        for _ in range(5):
            if check_widget('14221317'):
                print("Temple Trekking interface detected!")
                interface_found = True
                break
            wait_for_tick(1)
        
        if interface_found:
            while check_widget('14221317'):
                wait_for_tick(1)
                for _ in range(random.randint(1, 3)):
                    keyboard.press('space')
                    keyboard.release('space')
                    time.sleep(0.05)
            
            print("Successfully started Temple Trekking.")
            wait_for_tick(2)
            
            while True:
                if check_widget('15138821'):

                    print('Pressing space...')
                    
                    wait_for_tick(1)
                    for _ in range(random.randint(3, 5)):
                        keyboard.press('space')
                        time.sleep(random.uniform(0.039, 0.081))
                        keyboard.release('space')

                    while not click_widget(21561365):
                        wait_for_tick(1)
                        print("Clicked final Continue widget.")
                    return True
        else:
            print(f"Attempt {attempt}: No interface after 5 ticks. Retrying...")
            if attempt < max_attempts:
                wait_for_tick(2)
    
    print("Failed to start Temple Trekking after all attempts.")
    return False


while True:
    ensure_camera_settings(pitch=491, yaw=0, zoom=152)
    
    if is_in_temple_trekking_area():
        
        while True:
            check_tome = use_tome()
            print(check_tome)
            if not check_tome:
                break

        print("In starting area – starting new Temple Trek.")
        start_temple_trekking()
        wait_for_tick(10)
        continue

    broken_bridge = get_closest_object('13834', 'Inspect')
    if broken_bridge:
        if get_closest_game_object('1365', None, 10):
            print("Dead tree room detected.")
            dead_tree_room()
        else:
            print("Zombie room detected.")
            zombie_room()

    if get_closest_game_object('13843', None, 10):
        print("Swamp tree room detected.")
        swamp_tree_room()

    if get_closest_object('13831', 'Evade-event'):
        aggressive_npcs = [
            'riyl shadow', 'nail beast', 'swamp snake',
            'giant snail', 'vampyre juvinate', 'ghast'
        ]
        
        for npc_name in aggressive_npcs:
            if npc(name=npc_name):
                print(f"Detected {npc_name} – evading.")
                evade_event()
                break
    else:
        pass

    time.sleep(random.uniform(0.3, 0.8))