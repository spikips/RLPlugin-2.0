import time
import random
import keyboard
import math
import sys

from modules.core.plugin_client import inventory, stats as plugin_stats, interact_options, gear, player, inventory, game_object
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.utils.camera import camera
from modules.utils.logout import logout_and_break
from modules.utils.banking import get_all_widget_data

rl_x, rl_y = runelite_window(0, 0)

# Polygon points for the woodcutting area (WorldPoints x,y,plane=0)
AREA_POLYGON = [
    (2959, 3191),
    (2959, 3201),
    (2971, 3203),
    (2983, 3212),
    (2999, 3207),
    (2999, 3191),
    (2983, 3191),
    (2981, 3193),
    (2977, 3193),
    (2970, 3188),
    (2959, 3191)
]

WOODCUTTING_ANIMS = {879, 877, 875, 873, 871, 869, 867, 2846}  # Add more if needed

AXE_TIERS = {
    "bronze axe": 1,
    "iron axe": 1,
    "steel axe": 6,
    "black axe": 11,
    "mithril axe": 21,
    "adamant axe": 31,
    "rune axe": 41,
    "dragon axe": 61,
}

def point_in_polygon(x, y, polygon):
    """
    Ray-casting algorithm to check if point (x,y) is inside polygon.
    Counts horizontal ray intersections (odd=inside); efficient for simple polygons; assumes closed shape.
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

def get_tree_config(wc_level):
    """Determine tree IDs, target name based on Woodcutting level."""
    if wc_level < 15:
        print(f"Debug: Woodcutting level {wc_level} < 15, targeting regular trees")
        return "1276,1278", "Tree"
    elif wc_level < 30:
        print(f"Debug: Woodcutting level {wc_level} < 30, targeting oak trees")
        return "10820", "Oak tree"
    else:
        print(f"Debug: Woodcutting level {wc_level} >= 30, targeting willow trees")
        return "10819,10829,10831,10833", "Willow tree"

def has_suitable_axe(wc_level):
    """Check if we have a suitable axe in inventory or equipped."""
    # Check equipped (no inventory open needed for gear)
    gear_data = gear()
    if gear_data and 'data' in gear_data:
        for item in gear_data['data']:
            name = item.get('name', '').lower() if isinstance(item, dict) else item.lower()
            if name in AXE_TIERS and AXE_TIERS[name] <= wc_level:
                print(f"Debug: Found suitable axe (equipped): {name} (level {AXE_TIERS[name]})")
                return True
    # Ensure inventory open before checking inv
    if not ensure_inventory_open():
        print("Error: Could not open inventory to check for axes")
        return False
    inv = inventory()
    if inv and 'data' in inv:
        for item in inv['data']:
            name = item.get('name', '').lower() if isinstance(item, dict) else item.lower()
            if name in AXE_TIERS and AXE_TIERS[name] <= wc_level:
                print(f"Debug: Found suitable axe (inventory): {name} (level {AXE_TIERS[name]})")
                return True
    print("Debug: No suitable axe found")
    return False

def is_inventory_open():
    """Check if the inventory tab is open by checking the sprite ID of the inventory tab widget."""
    print("Debug: Checking if inventory is open...")
    widgets = get_all_widget_data()
    if widgets:
        print(f"Debug: Fetched {len(widgets)} widgets")
        for widget in widgets:
            widget_id = widget.get('id', 0) or widget.get('packedId', 0)
            if widget_id == 35913802:
                print(f"Debug: Found inventory tab ID 35913802 in widgets. Widget data: {widget}")
                sprite_id = widget.get('spriteId', -1)
                print(f"Debug: Found inventory tab widget (ID: {widget_id}) with spriteId: {sprite_id}")
                is_open = sprite_id == 1030
                print(f"Debug: Inventory open: {is_open} (spriteId == 1030)")
                return is_open
        print("Debug: Inventory tab ID 35913802 not found in widgets")
    else:
        print("Debug: No widgets data returned or invalid")
    return False

def ensure_inventory_open(max_attempts=3):
    """Ensure the inventory is open by checking and pressing F1 if needed, with retries."""
    focus_runelite_window()
    for attempt in range(1, max_attempts + 1):
        if is_inventory_open():
            print(f"Debug: Inventory is already open (attempt {attempt})")
            return True
        print(f"Debug: Inventory not open (attempt {attempt}), pressing F1")
        keyboard.press_and_release("f1")
        time.sleep(0.5)
    print(f"Debug: Failed to open inventory after {max_attempts} attempts")
    return False

def manage_axes(wc_level):
    """Drop lower tier axes from inventory if we have better ones available."""
    if not ensure_inventory_open():
        print("Error: Could not open inventory for managing axes")
        return

    # Find best axe tier usable at current level
    best_usable = max([tier for tier in AXE_TIERS.values() if tier <= wc_level], default=1)
    print(f"Debug: Best axe tier usable at level {wc_level}: {best_usable}")

    # Find all usable axes in equipped and inventory
    equipped_axes = []
    gear_data = gear()
    if gear_data and 'data' in gear_data:
        for item in gear_data['data']:
            name = item.get('name', '').lower() if isinstance(item, dict) else item.lower()
            if name in AXE_TIERS and AXE_TIERS[name] <= wc_level:
                equipped_axes.append(AXE_TIERS[name])

    inv_axes = []
    inv = inventory(middle_point=True)
    if inv and 'data' in inv:
        for item in inv['data']:
            name = item.get('name', '').lower() if isinstance(item, dict) else item.lower()
            if name in AXE_TIERS and AXE_TIERS[name] <= wc_level:
                inv_axes.append((AXE_TIERS[name], item))

    all_axes_tiers = equipped_axes + [tier for tier, _ in inv_axes]
    if not all_axes_tiers:
        print("Debug: No usable axes found; nothing to manage.")
        return

    best_owned = max(all_axes_tiers)
    print(f"Debug: Best owned axe tier: {best_owned}")

    # Drop lower tier axes from inventory only if better exists
    for tier, item in inv_axes:
        if tier < best_owned:
            point = item.get('random_clickpoint')
            if point:
                name = item.get('name', '').lower()
                keyboard.press('shift')
                mouse(point['x'] + rl_x, point['y'] + rl_y, button="left")
                keyboard.release('shift')
                time.sleep(random.uniform(0.5, 1))
                print(f"Dropped lower tier axe (tier {tier}): {name}")

def drop_logs():
    """Drop all logs from inventory in a zigzag pattern by holding shift and clicking."""
    if not ensure_inventory_open():
        print("Error: Could not open inventory for dropping logs")
        return
    logs = inventory(middle_point=True)
    if logs and 'data' in logs:
        logs_data = [log for log in logs['data'] if log.get('name', '').lower().endswith('logs')]
        if not logs_data:
            print("Debug: No logs found in inventory")
            return
        # Compute row and col based on unique middle_points
        unique_x = sorted(set(item['middle_point']['x'] for item in logs_data))
        unique_y = sorted(set(item['middle_point']['y'] for item in logs_data))
        col_map = {x: idx for idx, x in enumerate(unique_x)}
        row_map = {y: idx for idx, y in enumerate(unique_y)}
        for item in logs_data:
            item['col'] = col_map[item['middle_point']['x']]
            item['row'] = row_map[item['middle_point']['y']]
        # Sort in zigzag: by block (row//2), then col, then subrow (row%2)
        sorted_logs = sorted(logs_data, key=lambda d: (d['row'] // 2, d['col'], d['row'] % 2))
        print(f"Debug: Dropping {len(sorted_logs)} logs in zigzag order: {[(log['row'], log['col']) for log in sorted_logs]}")
        keyboard.press('shift')
        for log in sorted_logs:
            point = log.get('random_clickpoint')
            if point:
                print(f"Debug: Dropping log '{log.get('name')}' at row {log['row']}, col {log['col']}, coords ({point['x'] + rl_x}, {point['y'] + rl_y})")
                mouse(point['x'] + rl_x, point['y'] + rl_y, button="left", fast=True, sleep=True)
                time.sleep(random.uniform(0.01, 0.03))
                if not is_inventory_open():
                    print("Debug: Inventory closed during drop; re-opening")
                    if not ensure_inventory_open():
                        print("Error: Inventory closed and could not re-open during drop")
                        keyboard.release('shift')
                        return
        keyboard.release('shift')
    else:
        print("Debug: No inventory data available")

def chop_trees_in_polygon(wc_level):
    """Chop available trees in polygon until inventory full, preferring closest, only if clickable within client bounds and left-click is 'Chop down' for correct tree."""
    client_min_x = rl_x + 4
    client_min_y = rl_y + 4
    client_max_x = rl_x + 4 + 512
    client_max_y = rl_y + 4 + 334
    ids_str, target_name = get_tree_config(wc_level)
    expected_target = f"<col=ffff>{target_name}"
    print(f"Debug: Targeting IDs {ids_str} based on WC level {wc_level}, expected target: {expected_target}")
    drop_chance = 0.1 if wc_level < 15 else 0.5
    while not is_inventory_full():
        camera_data = player(camera=True).get('data', {}).get('camera', {})
        current_pitch = camera_data.get('pitch', 0)
        current_yaw = camera_data.get('yaw', 0)
        current_zoom = camera_data.get('zoom', 0)
        print(f"Debug: Current camera - Pitch: {current_pitch}, Yaw: {current_yaw}, Zoom: {current_zoom}")
        if abs(current_pitch - 512) > 20 or abs((current_yaw - 13) % 2048) > 20 or abs(current_zoom - 250) > 50:
            print("Debug: Camera not within tolerance; adjusting to default.")
            camera(pitch=512, yaw=13, zoom=250)
        else:
            print("Debug: Camera already within tolerance; skipping adjustment.")
        player_data = player(location=True)
        player_loc = player_data.get('data', {}).get('location', {})
        px, py = player_loc.get('x', 0), player_loc.get('y', 0)
        print(f"Debug: Player at ({px}, {py})")
        trees = game_object(object=ids_str, tile=True, middle_point=True, tile_radius=50)
        print(f"Debug: Fetched {len(trees.get('data', []))} potential trees")
        candidates = []
        for tree in trees.get('data', []):
            tx, ty = tree['tile']['x'], tree['tile']['y']
            if point_in_polygon(tx, ty, AREA_POLYGON):
                point = tree.get('middle_point')
                if point:
                    mx = point['x'] + rl_x
                    my = point['y'] + rl_y
                    if client_min_x <= mx <= client_max_x and client_min_y <= my <= client_max_y:
                        dist = math.hypot(tx - px, ty - py)
                        candidates.append((dist, target_name.lower(), tx, ty, mx, my, point['x'], point['y'], tree))
        print(f"Debug: {len(candidates)} clickable trees in polygon")
        if candidates:
            candidates.sort(key=lambda c: c[0])
            chopped = False
            for dist, t_type, tx, ty, mx, my, local_x, local_y, tree_data in candidates:
                print(f"Debug: Hovering over tree candidate at world ({tx}, {ty}), dist {dist:.1f} tiles (closest first), screen ({mx}, {my}). Tree data: {tree_data}")
                mouse(mx, my, fast=False)
                time.sleep(0.3)
                options_data = interact_options()
                print("Interact Options Data:", options_data)
                if options_data and 'data' in options_data and options_data['data']:
                    first_option = options_data['data'][0]
                    if first_option['option'] == 'Chop down' and first_option['target'] == expected_target:
                        print(f"Cutting {t_type} at level {wc_level} - Closest at world ({tx}, {ty}), dist {dist:.1f} tiles, screen ({mx}, {my}). Reason: Valid 'Chop down' option matched.")
                        mouse(mx, my, button="left")
                        start_time = time.time()
                        started = False
                        while time.time() - start_time < 10:
                            anim_data = player(animation=True)
                            anim = anim_data.get('data', {}).get('animation', -1)
                            if anim in WOODCUTTING_ANIMS:
                                print(f"Debug: Started woodcutting (anim: {anim})")
                                started = True
                                break
                            time.sleep(0.6)
                        if not started:
                            print("Debug: Failed to start woodcutting")
                            continue
                        while True:
                            anim_data = player(animation=True)
                            anim = anim_data.get('data', {}).get('animation', -1)
                            if anim == -1:
                                print("Debug: Stopped woodcutting")
                                break
                            time.sleep(0.6)
                        chopped = True
                        break
                    else:
                        print(f"Debug: Skipping tree at ({tx}, {ty}), dist {dist:.1f} tiles. Reason: No 'Chop down' or target mismatch (expected: {expected_target}, got: {first_option.get('target', 'None')}).")
            if chopped:
                # Check level after chop (XP gained)
                new_wc_level = plugin_stats().get('data', {}).get('Woodcutting', {}).get('level', 0)
                print(f"Debug: Post-chop WC level check: {new_wc_level}")
                if new_wc_level != wc_level:
                    print(f"Debug: Level changed from {wc_level} to {new_wc_level}, updating tree target")
                    return new_wc_level  # Return to update main loop
                if random.random() < drop_chance or is_inventory_full():
                    print("Debug: Dropping logs (random or full).")
                    drop_logs()
                if not is_inventory_open():
                    print("Debug: Inventory closed after chop; re-opening")
                    ensure_inventory_open()
            else:
                print(f"Debug: No tree with correct 'Chop down' left-click option.")
                time.sleep(1)
        else:
            print(f"Debug: No trees at current zoom; adjusting to zoom 135 and searching for 45 seconds")
            camera(pitch=512, yaw=13, zoom=135)
            start_time = time.time()
            found = False
            while time.time() - start_time < 45:
                trees = game_object(object=ids_str, tile=True, middle_point=True, tile_radius=50)
                candidates = []
                for tree in trees.get('data', []):
                    tx, ty = tree['tile']['x'], tree['tile']['y']
                    if point_in_polygon(tx, ty, AREA_POLYGON):
                        point = tree.get('middle_point')
                        if point:
                            mx = point['x'] + rl_x
                            my = point['y'] + rl_y
                            if client_min_x <= mx <= client_max_x and client_min_y <= my <= client_max_y:
                                dist = math.hypot(tx - px, ty - py)
                                candidates.append((dist, target_name.lower(), tx, ty, mx, my, point['x'], point['y'], tree))
                if candidates:
                    print(f"Debug: Found trees at zoom 135")
                    found = True
                    candidates.sort(key=lambda c: c[0])
                    chopped = False
                    for dist, t_type, tx, ty, mx, my, local_x, local_y, tree_data in candidates:
                        print(f"Debug: Hovering over tree candidate at world ({tx}, {ty}), dist {dist:.1f} tiles (closest first at zoom 135), screen ({mx}, {my}). Tree data: {tree_data}")
                        mouse(mx, my, fast=False)
                        time.sleep(0.3)
                        options_data = interact_options()
                        print("Interact Options Data:", options_data)
                        if options_data and 'data' in options_data and options_data['data']:
                            first_option = options_data['data'][0]
                            if first_option['option'] == 'Chop down' and first_option['target'] == expected_target:
                                print(f"Cutting {t_type} at level {wc_level} - at world ({tx}, {ty}), dist {dist:.1f} tiles, screen ({mx}, {my}) at zoom 135. Reason: Valid 'Chop down' option matched.")
                                mouse(mx, my, button="left")
                                start_time_chop = time.time()
                                started = False
                                while time.time() - start_time_chop < 10:
                                    anim_data = player(animation=True)
                                    anim = anim_data.get('data', {}).get('animation', -1)
                                    if anim in WOODCUTTING_ANIMS:
                                        print(f"Debug: Started woodcutting (anim: {anim})")
                                        started = True
                                        break
                                    time.sleep(0.6)
                                if not started:
                                    continue
                                while True:
                                    anim_data = player(animation=True)
                                    anim = anim_data.get('data', {}).get('animation', -1)
                                    if anim == -1:
                                        print("Debug: Stopped woodcutting")
                                        break
                                    time.sleep(0.6)
                                chopped = True
                                break
                            else:
                                print(f"Debug: Skipping tree at ({tx}, {ty}), dist {dist:.1f} tiles at zoom 135. Reason: No 'Chop down' or target mismatch (expected: {expected_target}, got: {first_option.get('target', 'None')}).")
                    if chopped:
                        # Check level after chop
                        new_wc_level = plugin_stats().get('data', {}).get('Woodcutting', {}).get('level', 0)
                        print(f"Debug: Post-chop WC level check at zoom 135: {new_wc_level}")
                        if new_wc_level != wc_level:
                            print(f"Debug: Level changed from {wc_level} to {new_wc_level}, updating tree target")
                            return new_wc_level
                        if random.random() < drop_chance or is_inventory_full():
                            print("Debug: Dropping logs (random or full) at zoom 135.")
                            drop_logs()
                        if not is_inventory_open():
                            print("Debug: Inventory closed after chop at zoom 135; re-opening")
                            ensure_inventory_open()
                    break
                time.sleep(0.1)
            if not found:
                print(f"Debug: No trees after 45s at zoom 135; adjusting to zoom 61 and searching once")
                camera(pitch=512, yaw=13, zoom=61)
                trees = game_object(object=ids_str, tile=True, middle_point=True, tile_radius=50)
                candidates = []
                for tree in trees.get('data', []):
                    tx, ty = tree['tile']['x'], tree['tile']['y']
                    if point_in_polygon(tx, ty, AREA_POLYGON):
                        point = tree.get('middle_point')
                        if point:
                            mx = point['x'] + rl_x
                            my = point['y'] + rl_y
                            if client_min_x <= mx <= client_max_x and client_min_y <= my <= client_max_y:
                                dist = math.hypot(tx - px, ty - py)
                                candidates.append((dist, target_name.lower(), tx, ty, mx, my, point['x'], point['y'], tree))
                if candidates:
                    print(f"Debug: Found trees at zoom 61")
                    candidates.sort(key=lambda c: c[0])
                    chopped = False
                    for dist, t_type, tx, ty, mx, my, local_x, local_y, tree_data in candidates:
                        print(f"Debug: Hovering over tree candidate at world ({tx}, {ty}), dist {dist:.1f} tiles (closest first at zoom 61), screen ({mx}, {my}). Tree data: {tree_data}")
                        mouse(mx, my, fast=False)
                        time.sleep(0.3)
                        options_data = interact_options()
                        print("Interact Options Data:", options_data)
                        if options_data and 'data' in options_data and options_data['data']:
                            first_option = options_data['data'][0]
                            if first_option['option'] == 'Chop down' and first_option['target'] == expected_target:
                                print(f"Cutting {t_type} at level {wc_level} - at world ({tx}, {ty}), dist {dist:.1f} tiles, screen ({mx}, {my}) at zoom 61. Reason: Valid 'Chop down' option matched.")
                                mouse(mx, my, button="left")
                                start_time_chop = time.time()
                                started = False
                                while time.time() - start_time_chop < 10:
                                    anim_data = player(animation=True)
                                    anim = anim_data.get('data', {}).get('animation', -1)
                                    if anim in WOODCUTTING_ANIMS:
                                        print(f"Debug: Started woodcutting (anim: {anim})")
                                        started = True
                                        break
                                    time.sleep(0.6)
                                if not started:
                                    continue
                                while True:
                                    anim_data = player(animation=True)
                                    anim = anim_data.get('data', {}).get('animation', -1)
                                    if anim == -1:
                                        print("Debug: Stopped woodcutting")
                                        break
                                    time.sleep(0.6)
                                chopped = True
                                break
                            else:
                                print(f"Debug: Skipping tree at ({tx}, {ty}), dist {dist:.1f} tiles at zoom 61. Reason: No 'Chop down' or target mismatch (expected: {expected_target}, got: {first_option.get('target', 'None')}).")
                    if chopped:
                        # Check level after chop
                        new_wc_level = plugin_stats().get('data', {}).get('Woodcutting', {}).get('level', 0)
                        print(f"Debug: Post-chop WC level check at zoom 61: {new_wc_level}")
                        if new_wc_level != wc_level:
                            print(f"Debug: Level changed from {wc_level} to {new_wc_level}, updating tree target")
                            return new_wc_level
                        if random.random() < drop_chance or is_inventory_full():
                            print("Debug: Dropping logs (random or full) at zoom 61.")
                            drop_logs()
                        if not is_inventory_open():
                            print("Debug: Inventory closed after chop at zoom 61; re-opening")
                            ensure_inventory_open()
                else:
                    print("Debug: No trees found even at zoom 61; exiting script")
                    sys.exit("No trees available")
            # If found at 135 or 61, continue loop (next iter will check camera again)
    return wc_level  # No level change

def is_inventory_full():
    """Check if inventory has 28 items."""
    inv = inventory()
    full = len(inv.get('data', [])) >= 28
    print(f"Debug: Inventory size: {len(inv.get('data', []))}, full: {full}")
    return full

def woodcutting():
    """Main loop: manage axes -> chop in polygon -> break/repeat."""
    wc_level = plugin_stats().get('data', {}).get('Woodcutting', {}).get('level', 0)
    print(f"Debug: Initial WC level: {wc_level}")
    while True:
        if not has_suitable_axe(wc_level):
            print("Debug: No suitable axe found; acquire one.")
            sys.exit("Exiting script due to no suitable axe.")
        if is_inventory_full():
            print("Debug: Inventory full at start of loop; dropping logs.")
            drop_logs()
        manage_axes(wc_level)
        new_wc_level = chop_trees_in_polygon(wc_level)
        if new_wc_level != wc_level:
            wc_level = new_wc_level
            print(f"Debug: Updated WC level in main loop to {wc_level}")
        if random.random() < 0.01:
            sleep_time = random.uniform(15, 180)
            print(f"Debug: Short AFK sleep for {sleep_time:.1f} seconds")
            time.sleep(sleep_time)
        else:
            break_chance = 0.001 if wc_level < 15 else 0.0025
            if random.random() < break_chance:
                logout_and_break(random.uniform(30, 90))

# Example usage
# time.sleep(1)
# woodcutting()