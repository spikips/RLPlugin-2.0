# crocodile.py
# A script for automating a crocodile slayer task using a cannon in Old School RuneScape via RuneLite plugin.
# Uses reliable object detection via get_closest_object for cannon existence/placement.
# Uses cannon_data() for ammo count to decide reload.
# Prints full cannon_info every loop for debug.
# If no cannon base in inventory, assumes cannon is already placed.
# Runs in a loop until slayer task is completed (slayer_task_remaining == 0).
# Picks up the cannon when task is completed.

import time
import random

# Core imports
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.core.plugin_client import cannon_data, minimap_tile_point, player, inventory, slayer_task_remaining

from modules.core.mouse_control import move, right_click
# Player data imports
from modules.player_data.cannon import click_cannon
from modules.player_data.prayer.toggle_prayer import toggle_prayer

# Object data imports
from modules.object_data.object import get_closest_object

# Utils imports
from modules.utils.check_if_in_tile import check_if_in_tile, click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.inventory import click_inventory

from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.camera import camera


# Constants
CANNON_TILE = (3191, 2825, 0)  # Cannon position (x, y, plane)
STAND_TILE = (3191, 2823, 0)   # Standing position (x, y, plane)
CANNON_NAME = "Dwarf multicannon"
LOOT_ITEMS = []  # No items to loot
LOOT_RADIUS = 15
CANNON_PLACE_TIMEOUT_TICKS = 40
MAX_PLACEMENT_TRIES = 3

def is_cannon_placed():
    """Check if cannon exists using object detection (Fire or Pick-up option)."""
    fire_obj = get_closest_object(CANNON_NAME, "Fire", tile=CANNON_TILE, radius=10)
    pickup_obj = get_closest_object(CANNON_NAME, "Pick-up", tile=CANNON_TILE, radius=10)
    placed = fire_obj is not None or pickup_obj is not None
    print(f"CANNON OBJECT CHECK: placed={placed}, fire_available={fire_obj is not None}, pickup_available={pickup_obj is not None}")
    return placed

def place_cannon():
    # Move to cannon tile (required for placement)
    on_tile = check_if_in_tile(CANNON_TILE[0], CANNON_TILE[1], CANNON_TILE[2], click=True)
    if not on_tile:
        print("Standard movement failed. Falling back to minimap click with zoom 5.")
        click_minimap_tile(CANNON_TILE[0], CANNON_TILE[1], target_zoom=5.0)
        wait_till_character_stopped_moving()

        player_pos = player(location=True).get('data', {}).get('location', {})
        if (player_pos.get('x'), player_pos.get('y'), player_pos.get('plane')) != CANNON_TILE:
            print("Minimap click failed. Falling back to right-click 'Walk here'.")
            click_tile(CANNON_TILE[0], CANNON_TILE[1])
            wait_till_character_stopped_moving()


    # Try to click cannon base
    if not click_inventory("Cannon base"):
        print("No 'Cannon base' in inventory - assuming cannon is already placed.")
        return True  # Assume placed if no base

    # Wait for empty cannon ('Fire' option appears)
    waited_ticks = 0
    while waited_ticks < CANNON_PLACE_TIMEOUT_TICKS:
        if get_closest_object(CANNON_NAME, "Fire", tile=CANNON_TILE, radius=10):
            print("Cannon placed successfully ('Fire' option detected).")
            wait_for_next_tick(1)
            click_cannon('Fire', exact_tile=CANNON_TILE)  # Load immediately after placement
            return True
        wait_for_next_tick(1)
        waited_ticks += 1

    print("Timeout waiting for cannon ('Fire' option) to appear after placement.")
    return False

def check_prayer_level():
    p_data = player(prayer=True)
    if not p_data or 'data' not in p_data:
        return 100
    return p_data['data'].get('prayer', 100)

def has_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False
    for item in inv_data['data']:
        name = item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            return True
    return False


def drink_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        return False
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            mp = inv_item['middle_point']
            sx, sy = runelite_window(mp['x'], mp['y'])
            move(sx, sy, fast=True, sleep=True, button='left')
            print(f"Drank {name}")
            wait_for_tick(1)
            return True
    return False

def main():
    # Focus RuneLite window at start
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
    # Check login state and handle login if needed
    
    from modules.utils.logout import check_login_state_and_login  # For login handling
    check_login_state_and_login()

    # Camera setup at start (random pitch/yaw, fixed zoom)
    print("Setting up camera...")
    camera(
        pitch=random.randint(300, 512),
        yaw=random.randint(600, 1000),
        zoom=random.randint(250, 300)
    )

    # Initial random thresholds
    prayer_threshold = random.randint(15, 25)
    cannon_threshold = random.randint(5, 25)
    print(f"Initial prayer drink threshold set to {prayer_threshold}")
    print(f"Initial cannon reload threshold set to {cannon_threshold}")

    print("Starting crocodile slayer task with cannon.")

    while True:
        # Check slayer task remaining
        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            print("Task completed - navigating to Slayer Master Vannaka in Edgeville Dungeon.")
            if is_cannon_placed():
                if click_cannon('Pick-up', exact_tile=CANNON_TILE):
                    print("Cannon picked up.")
                else:
                    print("Failed to pick up cannon.")
            print("Navigation complete - script ending (restart for new task).")
            break

        # Get and print cannon_info every loop
        raw_cannon_info = cannon_data()
        cannon_info = raw_cannon_info.get('data', {}) if raw_cannon_info else {}

        # Reliable object-based detection for existence
        cannon_placed = is_cannon_placed()

        if not cannon_placed:
            print("No cannon detected (object check). Attempting to place one.")
            for attempt in range(1, MAX_PLACEMENT_TRIES + 1):
                print(f"Placement attempt {attempt}/{MAX_PLACEMENT_TRIES}")
                if place_cannon():
                    # Force load after successful placement
                    if click_cannon('Fire', exact_tile=CANNON_TILE):
                        print("Cannon loaded after placement.")
                    else:
                        print("Failed to load cannon after placement.")
                    break
                else:
                    print("Placement failed. Retrying..." if attempt < MAX_PLACEMENT_TRIES else "Max attempts reached.")
                    time.sleep(2)

            # Always return to stand tile after placement attempts
            check_if_in_tile(STAND_TILE[0], STAND_TILE[1], STAND_TILE[2], click=True)

        # Ensure standing position
        if not check_if_in_tile(STAND_TILE[0], STAND_TILE[1], STAND_TILE[2], click=True):
            print("Standard movement to stand tile failed. Falling back to minimap click with zoom 5.")
            click_tile(STAND_TILE[0], STAND_TILE[1])
            # click_minimap_tile(STAND_TILE[0], STAND_TILE[1], target_zoom=5.0)
            wait_till_character_stopped_moving()

        # Prayer management with dynamic threshold
        toggle_prayer('PROTECT_FROM_MELEE', activate=True)
        current_prayer = check_prayer_level()
        if current_prayer <= prayer_threshold:
            if has_prayer_potion():
                drink_prayer_potion()
                print(f"Drank prayer potion (level {current_prayer} <= threshold {prayer_threshold})")
                # Choose new random threshold for next drink
                prayer_threshold = random.randint(15, 25)
                print(f"New prayer drink threshold set to {prayer_threshold}")
            else:
                print("Prayer low and no potion available")

        # Cannon reload with dynamic threshold
        ball_count = cannon_info.get('ammo', 0)
        if cannon_placed and ball_count <= cannon_threshold:
            if click_cannon('Fire', exact_tile=CANNON_TILE):
                print(f"Cannon reloaded (ammo {ball_count} <= threshold {cannon_threshold})")
                # Choose new random threshold for next reload
                cannon_threshold = random.randint(5, 25)
                print(f"New cannon reload threshold set to {cannon_threshold}")
            else:
                if click_cannon('repair', exact_tile=CANNON_TILE):
                    print('cannon repaired, reloading')
                    for _ in range(10):
                        if click_cannon('Fire', exact_tile=CANNON_TILE):
                            print(f"Cannon reloaded after repair (ammo {ball_count} <= threshold {cannon_threshold})")
                            # Choose new random threshold for next reload
                            cannon_threshold = random.randint(5, 25)
                            print(f"New cannon reload threshold set to {cannon_threshold}")
                            break
                        wait_for_next_tick(1)
                else:
                    print("Failed to reload or repair cannon.")

        # Tick wait
        wait_for_next_tick(1)


# drink_prayer_potion()
if __name__ == "__main__":
    main()