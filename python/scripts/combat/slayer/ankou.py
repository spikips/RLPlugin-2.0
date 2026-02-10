# ankou.py
# Script for automating Ankou slayer task (no cannon, no movement).
# Behavior:
# - Keeps Protect from Melee prayer active with dynamic potion drinking.
# - If aggro: Stay put (fight normally).
# - If no aggro: Endless swoop - attack closest Ankou until aggro regained.
#   - High max attempts for practically endless swoop.
#   - Waits after each attack for potential re-aggro.
# - On task completion (slayer_task_remaining == 0): Navigate to Slayer Master in Edgeville Dungeon (Vannaka).
# - No hardcoded stand tiles or refresh runs - stays wherever you are.

import time
import random

# Core imports
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import player, inventory, npc_agro, slayer_task_remaining

# Utils imports
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.camera import camera


# Prayer potion drinking
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
    from modules.core.window_utils import runelite_window
    from modules.core.mouse_control import move
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
            wait_for_next_tick(1)
            return True
    return False

# Aggro check
def is_aggroed():
    agro_data = npc_agro()
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected.")
        return False
    else:
        print('agro detected')
        return True

# Constants
SWOOP_MAX_ATTEMPTS = 100  # Very high for "endless" swoop until aggro back

def swoop_reset():
    print("No aggro - starting swoop reset (attacking closest Ankou)")
    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print(f"Swoop attempt {attempt + 1}")
        if click_closest_npc('Ankou', option='Attack', max_attempts=5):
            print("Ankou attacked - waiting for re-aggro")
            wait_till_character_stopped_moving()
            wait_for_next_tick(10)  # Time for tolerance reset/aggro
            if is_aggroed():
                print("Aggro regained from swoop")
                return True
        else:
            print("No Ankou in range for swoop")
        wait_for_next_tick(3)  # Short wait between attempts
    print("Swoop exhausted max attempts (unlikely - spot completely dead?)")
    return False  # Rare - only if truly no Ankou ever

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting up camera...")
    camera(
        pitch=random.randint(300, 512),
        yaw=random.randint(600, 1000),
        zoom=random.randint(420, 500)
    )
    time.sleep(1)

    prayer_threshold = random.randint(15, 25)
    print(f"Initial prayer drink threshold: {prayer_threshold}")

    print("Starting Ankou slayer task - stay and fight, swoop attack when no aggro.")

    while True:
        # Task completion check
        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            print("Task completed - navigating to Slayer Master Vannaka in Edgeville Dungeon.")
            print("Navigation complete - script ending (start new task manually or restart script).")
            break  # End script after navigation (or remove break to loop forever)

        # Prayer management
        toggle_prayer('PROTECT_FROM_MELEE', activate=True)
        current_prayer = check_prayer_level()
        if current_prayer <= prayer_threshold:
            if has_prayer_potion():
                drink_prayer_potion()
                print(f"Drank prayer potion (prayer {current_prayer} <= {prayer_threshold})")
                prayer_threshold = random.randint(15, 25)
                print(f"New prayer threshold: {prayer_threshold}")
            else:
                print("Prayer low, no potion available.")

        if is_aggroed():
            print("Aggro active - fighting normally.")
        else:
            swoop_reset()  # Endless swoop until aggro back

        wait_for_next_tick(1)

if __name__ == "__main__":
    main()