import time
import random
from typing import Dict, Optional

from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.core.plugin_client import player, pick, interact_options, gametick, inventory
from modules.core.mouse_control import move, get_cursor_pos
from modules.core.window_utils import runelite_window


def normalize_item_name(name: str) -> str:
    """Remove dose indicators and normalize for comparison."""
    return name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()


def clean_target_name(target: str) -> str:
    """Remove color tags and quantity suffixes (e.g., ' x 5') from menu target names."""
    if target.startswith('<col='):
        end_idx = target.find('>')
        if end_idx != -1:
            target = target[end_idx + 1:]
    if ' x ' in target:
        target = target.split(' x ')[0]
    return target.strip()


def can_pick_item(item_name: str) -> bool:
    """Check if there's space in inventory or if the item can stack."""
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False

    items = inv_data['data']
    occupied_slots = len(items)
    normalized_name = normalize_item_name(item_name)

    has_stackable = any(
        normalize_item_name(inv_item.get('item', '')) == normalized_name
        for inv_item in items
    )

    return occupied_slots < 28 or has_stackable


def wait_for_next_tick(num_ticks: int = 1) -> None:
    """Wait for a specified number of game ticks."""
    current_tick = gametick().get('data', 0)
    target_tick = current_tick + num_ticks
    while gametick().get('data', 0) < target_tick:
        time.sleep(0.05)


def wait_for_player_to_stop_moving(max_ticks: int = 20) -> bool:
    """Wait until player is idle (stable position and animation -1)."""
    end_tick = gametick().get('data', 0) + max_ticks
    last_position = None

    while gametick().get('data', 0) < end_tick:
        p_data = player(location=True, animation=True)
        if p_data and 'data' in p_data:
            loc = p_data['data'].get('location', {})
            anim = p_data['data'].get('animation', -1)
            pos = (loc.get('x'), loc.get('y'))
            if last_position == pos and anim == -1:
                return True
            last_position = pos
        time.sleep(0.1)
    return False


def pickup_closest_ground_item(item_name: str, tile_radius: int = 10) -> bool:
    """
    Generalized function to pick up the closest ground item matching the given name.
    Handles:
      - Hover check for direct left-click 'Take'
      - Right-click menu selection if needed
      - Walking to the item (clicking ground items auto-paths)
      - Waiting for movement to stop and loot to register
      - Retries when standing on the tile (common loot stacking issue)
      - Inventory full check
    
    Returns True if the item was successfully detected in inventory after pickup.
    """
    normalized_search = normalize_item_name(item_name)

    # Get player position
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        print("Failed to get player location.")
        return False
    loc = p_data['data'].get('location', {})
    player_x, player_y = loc.get('x'), loc.get('y')
    if player_x is None or player_y is None:
        return False

    # Get matching ground items
    ground_data = pick(player_x, player_y, size=tile_radius, item=item_name)
    if not ground_data or 'data' not in ground_data or not ground_data['data'].get('items'):
        return False

    items = ground_data['data']['items']

    # Sort by Manhattan distance (good enough and fast)
    def dist(item_dict: Dict) -> int:
        tx = item_dict.get('tile', {}).get('x', 0)
        ty = item_dict.get('tile', {}).get('y', 0)
        return abs(tx - player_x) + abs(ty - player_y)

    items.sort(key=dist)
    target_item = items[0]
    tile_x = target_item['tile']['x']
    tile_y = target_item['tile']['y']
    distance = dist(target_item)
    on_tile = distance == 0

    if not can_pick_item(item_name):
        print(f"Inventory full or no space for {item_name}.")
        return False

    # Get current quantity for stackable items
    current_qty = 0
    inv_data = inventory(item=item_name)
    if inv_data and 'data' in inv_data:
        for inv_item in inv_data['data']:
            if normalize_item_name(inv_item.get('item', '')) == normalized_search:
                current_qty = inv_item.get('quantity', 0)
                break

    print(f"Attempting to pick up closest {item_name} (distance: {distance}, current qty: {current_qty})")


    mp = target_item['middle_point']
    screen_x, screen_y = runelite_window(mp['x'], mp['y'])

    # Hover
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.15, 0.35))

    # Check hover menu for direct "Take"
    hover_data = interact_options().get('data', [])
    can_left_click = False
    if hover_data:
        top = hover_data[0]
        option = top.get('option', '').lower()
        target_name = clean_target_name(top.get('target', ''))
        if option.startswith('take') and normalized_search in normalize_item_name(target_name):
            can_left_click = True

    if can_left_click:
        print("  Left-clicking (Take is top option)")
        move(button='left', fast=True, sleep=True)
    else:
        print("  Right-clicking to open menu")
        move(button='right', fast=True, sleep=False)
        time.sleep(random.uniform(0.1, 0.25))

        menu_data = interact_options().get('data', [])
        take_entry = None
        for entry in menu_data:
            option = entry.get('option', '').lower()
            target_name = clean_target_name(entry.get('target', ''))
            if option.startswith('take') and normalized_search in normalize_item_name(target_name):
                take_entry = entry
                break

        if not take_entry:
            print("  No 'Take' option found – moving mouse away")
            cx, cy = get_cursor_pos()
            move(cx + random.randint(150, 300), cy + random.randint(-100, 100), fast=False)

            menu_mp = take_entry['middle_point']
            mx, my = runelite_window(menu_mp['x'], menu_mp['y'])
            click_x = mx + random.randint(-12, 12)
            click_y = my + random.randint(-4, 4)
            move(click_x, click_y, fast=True, button='left', sleep=True)

        # Post-click waiting
        if distance > 0:
            print("  Waiting for walking to complete")
            if not wait_for_player_to_stop_moving():
                print("  Timed out waiting for movement stop – retrying")
            wait_for_next_tick(2)  # Extra buffer for loot spawn
        else:
            wait_for_next_tick(3 if on_tile else 2)

        # Check if item appeared / quantity increased
        new_qty = current_qty
        for _ in range(6):  # Poll briefly
            inv_data = inventory(item=item_name)
            if inv_data and 'data' in inv_data:
                for inv_item in inv_data['data']:
                    if normalize_item_name(inv_item.get('item', '')) == normalized_search:
                        new_qty = inv_item.get('quantity', 0)
                        break
            if new_qty > current_qty:
                print(f"  Successfully picked up {item_name} (new qty: {new_qty})")
                return True
            time.sleep(0.1)

        print("  Item not detected in inventory")


    wait_till_character_stopped_moving(required_idle_ticks=1)
    return False


def loot_all_ground_items(item_name: str, tile_radius: int = 10, delay_range: tuple = (wait_for_next_tick())) -> int:
    """
    Convenience wrapper to repeatedly pick up all matching ground items.
    Returns the total number picked up.
    """
    count = 0
    while pickup_closest_ground_item(item_name, tile_radius):
        count += 1
        time.sleep(random.uniform(*delay_range))
    return count

# pickup_closest_ground_item("Mark of grace", tile_radius=15)
