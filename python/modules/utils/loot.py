# loot.py - Updated with lazy import for runelite_window to avoid startup hang

import time
import random
from typing import Dict, List

from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.core.plugin_client import player, pick, interact_options, gametick, inventory
from modules.core.mouse_control import move, get_cursor_pos

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
        normalize_item_name(inv_item.get('name', '')) == normalized_name
        for inv_item in items
    )

    return occupied_slots < 28 or has_stackable

def pickup_closest_ground_item(item_name: str, tile_radius: int = 10) -> bool:
    from modules.core.window_utils import runelite_window

    normalized = normalize_item_name(item_name)
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return False
    loc = p_data['data'].get('location', {})
    px, py = loc.get('x'), loc.get('y')
    if px is None or py is None:
        return False

    ground_data = pick(px, py, size=tile_radius, item=item_name)
    items = ground_data.get('data', {}).get('items', []) if ground_data else []
    if not items:
        return False

    # sort by Manhattan distance
    items.sort(key=lambda i: abs(i['tile']['x'] - px) + abs(i['tile']['y'] - py))
    target = items[0]

    if not can_pick_item(item_name):
        return False

    print(f"Attempting to pick up closest {item_name}")

    # === mouse move + click logic (with safety) ===
    mp = target.get('middle_point')
    if not mp:
        return False
    sx, sy = runelite_window(mp['x'], mp['y'])
    move(sx, sy, fast=True, sleep=True)
    time.sleep(random.uniform(0.15, 0.35))

    # hover check
    hover = interact_options().get('data', [])
    can_left = False
    if hover:
        top = hover[0]
        opt = top.get('option', '').lower()
        tgt = clean_target_name(top.get('target', ''))
        if opt.startswith('take') and normalize_item_name(tgt) == normalized:
            can_left = True

    if can_left:
        move(button='left', fast=True, sleep=True)
    else:
        move(button='right', fast=True, sleep=False)
        time.sleep(random.uniform(0.1, 0.25))
        menu = interact_options().get('data', [])
        for entry in menu:
            if (entry.get('option', '').lower().startswith('take') and
                normalize_item_name(clean_target_name(entry.get('target', ''))) == normalized):
                mx, my = runelite_window(entry['middle_point']['x'], entry['middle_point']['y'])
                move(mx + random.randint(-12, 12), my + random.randint(-4, 4),
                     fast=True, button='left', sleep=True)
                break
        else:
            return False  # no take option found

    wait_for_next_tick(3)

    # === NEW: verify it actually disappeared ===
    return not has_ground_items([item_name], tile_radius=3)

def loot_all_ground_items(item_name: str, tile_radius: int = 10, delay_range: tuple = (0.2, 0.5)) -> int:
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


def has_ground_items(item_list: List[str], tile_radius: int = 15) -> bool:
    """
    Check if any items from the provided list are present on the ground within tile_radius.
    Returns True if at least one matching item is found, False otherwise.
    Uses normalized names for comparison (ignores doses, case, etc.).
    """
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return False
    loc = p_data['data'].get('location', {})
    player_x, player_y = loc.get('x'), loc.get('y')
    if player_x is None or player_y is None:
        return False

    # Normalize once + use set for O(1) lookup
    normalized_set = {normalize_item_name(name) for name in item_list}

    # Fetch ALL ground items in the area ONCE (no item filter)
    ground_data = pick(player_x, player_y, size=tile_radius)
    if not ground_data or 'data' not in ground_data:
        return False

    items = ground_data['data'].get('items', [])
    for ground_item in items:
        ground_name = ground_item.get('name', '')
        if normalize_item_name(ground_name) in normalized_set:
            print(f"Found ground item matching '{ground_name}'")
            return True

    return False


# loot_all_ground_items()