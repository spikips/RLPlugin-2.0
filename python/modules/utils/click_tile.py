# click_tile.py
# Final pure ground click using existing 'tile' function.
# Key features:
# - tile_radius=0: Exact tile only (fails if not visible).
# - tile_radius>0: Picks the visible tile closest (manhattan) to center.
# - NO randomization at all - clicks exact middle_point pixel.
# - Debug prints show chosen world tile + distance from target.
# - Strict bounds clip 0-515 x 0-337.

import math
import re
from modules.core.plugin_client import interact_options, player, tile, walkable_tile
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.select_menu_option import select_menu_option
import time
import random

def click_tile(x: int, y: int, plane: int = 0, action: str = "Walk here", tile_radius: int = 20, right_click: bool = False) -> bool:
    """
    Clicks on the specified tile using main-screen click if possible.
    - tile_radius now strictly controls the search radius around the target for visible/on-screen walkable tiles.
    - Always prefers the exact target tile if visible.
    - If exact tile is off-screen, picks the closest visible walkable tile to the target within the exact radius provided.
    - If no visible tile found within radius -> falls back to click_minimap_tile.
    """
    target_base = (x, y, plane)
    print(f"Target base tile: {target_base}, search radius: {tile_radius}")

    # Get player position
    pl_data = player(location=True)
    if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
        print("Failed to fetch player location")
        return False
    loc = pl_data['data']['location']
    px, py, pplane = loc['x'], loc['y'], loc['plane']
    if pplane != plane:
        print("Plane mismatch")
        return False

    dist_to_target = math.hypot(x - px, y - py)
    print(f"Distance to target: {dist_to_target:.2f} tiles")

    if dist_to_target < 1:
        print("Already on target tile")
        return True

    # Use exactly the provided tile_radius for both API calls (faster, no oversized search)
    tile_data = tile(tile_x=x, tile_y=y, tile_radius=tile_radius, middle_point=True).get('data', [])
    walkable_data = walkable_tile(x, y, tile_radius=tile_radius, middle_point=False).get('data', [])

    # Candidates: visible (has middle_point) + walkable + within exact tile_radius of target
    candidates = []
    for t in tile_data:
        if 'middle_point' not in t:
            continue
        if not any(w['x'] == t['x'] and w['y'] == t['y'] and w['plane'] == plane for w in walkable_data):
            continue
        dist_from_target = math.hypot(t['x'] - x, t['y'] - y)
        if dist_from_target > tile_radius:
            continue
        candidates.append(t)

    if not candidates:
        print(f"No visible walkable tile within exact radius {tile_radius} -> falling back to minimap click")
        # Minimap fallback using your helper
        success = click_minimap_tile(
            x,
            y,
            rand_x=3,
            rand_y=3,
            target_zoom=2.0
        )
        if success:
            print("Minimap click successful")
            return True
        print("Minimap click failed")
        return False

    # Prefer exact tile first, then closest to target
    candidates.sort(key=lambda t: (0 if (t['x'], t['y']) == (x, y) else 1, math.hypot(t['x'] - x, t['y'] - y)))

    selected_tile = candidates[0]
    print(f"Selected tile: ({selected_tile['x']}, {selected_tile['y']}), distance from target: {math.hypot(selected_tile['x'] - x, selected_tile['y'] - y):.2f}")

    canvas_x = selected_tile['middle_point']['x']
    canvas_y = selected_tile['middle_point']['y']

    rl_x, rl_y = runelite_window(0, 0)
    screen_x = rl_x + canvas_x
    screen_y = rl_y + canvas_y

    # Hover to load options
    print(f"Hovering to x: {screen_x}, y: {screen_y}")
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.05, 0.12))

    options = interact_options().get('data', [])
    if not options:
        print("No interaction options after hover")
        return False

    action_normalized = ' '.join(action.lower().split())

    matched_option = None
    for opt in options:
        opt_target_clean = re.sub(r'<[^>]+>', '', opt['target']).lower()
        opt_combined = f"{opt['option'].lower()} {opt_target_clean}".strip()
        if opt['option'].lower() == action_normalized or opt_combined == action_normalized:
            matched_option = opt
            break

    if not matched_option:
        print(f"No '{action}' option found. Available: {[f'{o['option']} {re.sub(r'<[^>]+>', '', o['target'])}' for o in options]}")
        return False

    first_opt = options[0]
    first_target_clean = re.sub(r'<[^>]+>', '', first_opt['target']).lower()
    first_combined = f"{first_opt['option'].lower()} {first_target_clean}".strip()
    is_default = (first_opt['option'].lower() == action_normalized or first_combined == action_normalized)

    if is_default and not right_click:
        move(screen_x, screen_y, button='left', fast=True, sleep=True)
        print(f"Left-clicked tile ({selected_tile['x']}, {selected_tile['y']}) for default '{action}'")
    else:
        move(screen_x, screen_y, button='right', fast=True, sleep=True)
        time.sleep(random.uniform(0.05, 0.1))
        opt_x = rl_x + matched_option['middle_point']['x']
        opt_y = rl_y + matched_option['middle_point']['y']
        move(opt_x, opt_y, button='left', fast=True, sleep=True)
        print(f"Right-clicked and selected '{action}' on tile ({selected_tile['x']}, {selected_tile['y']})")

    return True