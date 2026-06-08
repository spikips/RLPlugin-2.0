# loot.py - Updated with lazy import for runelite_window to avoid startup hang

import time
import random
from typing import Dict, List

from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.core.plugin_client import player, pick, interact_options, gametick, inventory
from modules.core.mouse_control import move, get_cursor_pos

def normalize_item_name(name: str) -> str:
    """Remove dose indicators, quantity suffixes like (19), and normalize for comparison."""
    name = name.lower()
    # Remove dose indicators
    for dose in ['(4)', '(3)', '(2)', '(1)']:
        name = name.replace(dose, '')
    # Remove trailing quantity like " (19)" or "(19)"
    import re
    name = re.sub(r'\s*\(\d+\)\s*$', '', name)
    return name.strip()

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
        print("[DEBUG] No player data")
        return False

    loc = p_data['data'].get('location', {})
    px, py = loc.get('x'), loc.get('y')
    if px is None or py is None:
        print("[DEBUG] No player location")
        return False

    ground_data = pick(px, py, size=tile_radius, item=item_name)
    items = ground_data.get('data', {}).get('items', []) if ground_data else []
    if not items:
        print(f"[DEBUG] No ground items found for '{item_name}'")
        return False

    items.sort(key=lambda i: abs(i['tile']['x'] - px) + abs(i['tile']['y'] - py))
    target = items[0]

    if not can_pick_item(item_name):
        print("[DEBUG] Inventory full / cannot pick")
        return False

    print(f"\n[DEBUG] === pickup_closest_ground_item START: '{item_name}' ===")
    print(f"[DEBUG] normalized = '{normalized}'")

    MAX_TRIES = 3

    for attempt in range(1, MAX_TRIES + 1):
        print(f"\n[DEBUG] === Attempt {attempt}/{MAX_TRIES} for '{item_name}' ===")

        # Re-scan every attempt in case position changed slightly
        ground_data = pick(px, py, size=tile_radius, item=item_name)
        items = ground_data.get('data', {}).get('items', []) if ground_data else []
        if not items:
            print(f"[DEBUG] Item '{item_name}' no longer visible on attempt {attempt}")
            return False

        items.sort(key=lambda i: abs(i['tile']['x'] - px) + abs(i['tile']['y'] - py))
        target = items[0]

        mp = target.get('middle_point')
        if not mp:
            print("[DEBUG] No middle_point on this attempt")
            continue

        print(f"[DEBUG] middle_point: x={mp['x']}, y={mp['y']}")
        sx, sy = runelite_window(mp['x'], mp['y'])

        # small jitter
        sx += random.randint(-1, 1)
        sy += random.randint(-1, 1)
        print(f"[DEBUG] target with jitter: ({sx}, {sy})")

        print("[DEBUG] Moving mouse + hovering...")
        move(sx, sy)
        time.sleep(random.uniform(0.075, 0.12))

        # Read top hover
        print("[DEBUG] Reading hover...")
        hover = interact_options().get('data', []) or []

        top_opt = ""
        top_norm = ""

        if hover:
            t = hover[0]
            top_opt = t.get('option', '').lower().strip()
            tgt = clean_target_name(t.get('target', ''))
            top_norm = normalize_item_name(tgt)
            print(f"[DEBUG] HOVER → option='{top_opt}' | target_norm='{top_norm}'")
        else:
            print("[DEBUG] HOVER → no data")

        # Decision
        do_left = (top_opt == 'take' and top_norm == normalized) or (top_norm == normalized)
        print(f"[DEBUG] do_left = {do_left}")

        if do_left:
            print("[DEBUG] LEFT CLICK")
            cur = get_cursor_pos()
            move(cur[0], cur[1], button='left')
        else:
            print("[DEBUG] RIGHT CLICK")
            move(button='right')
            time.sleep(random.uniform(0.13, 0.18))

            print("[DEBUG] Reading menu...")
            menu = interact_options().get('data', []) or []
            print(f"[DEBUG] Menu entries:")
            for i, e in enumerate(menu):
                print(f"  [{i}] option='{e.get('option', '')}' | target='{e.get('target', '')}'")

            clicked = False
            for e in menu:
                o = e.get('option', '').lower().strip()
                t = clean_target_name(e.get('target', ''))
                tn = normalize_item_name(t)
                if (o.startswith('take') and tn == normalized) or (tn == normalized):
                    mx, my = runelite_window(e['middle_point']['x'], e['middle_point']['y'])
                    print(f"[DEBUG] Clicking Take at ({mx}, {my})")
                    move(mx + random.randint(-1, 1), my + random.randint(-1, 1), button='left', fast=True, sleep=True)
                    clicked = True
                    break

            if not clicked:
                print("[DEBUG] No Take found in menu this attempt")
                # still fall through to misclick handling below

        print("[DEBUG] Waiting 1 ticks...")
        wait_for_next_tick(1)

        still_there = has_ground_items([item_name], tile_radius=3)
        print(f"[DEBUG] Item still on ground after attempt {attempt}? {still_there}")

        if not still_there:
            print(f"[DEBUG] === SUCCESS on attempt {attempt} ===\n")
            return True

        # === Misclick handling ===
        if attempt < MAX_TRIES:
            cur = get_cursor_pos()
            print(f"[DEBUG] Misclick detected. Moving mouse -50 Y to clear interface (from {cur})")
            move(cur[0], cur[1] - 50)          # move mouse up 50 pixels to clear hover/menu
            time.sleep(0.08)
        else:
            print(f"[DEBUG] === FAILED after {MAX_TRIES} attempts ===\n")
            return False

    return False

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