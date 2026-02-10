# sand_crabs.py
# Final script for Sand Crabs without cannon.
# Behavior (fixed to match exact description):
# - If aggro: Stay put, reset counter.
# - If no aggro: Move to the other local tile.
#   - Wait until stopped + long wait_for_next_tick(20) (~12 seconds) for crabs to potentially re-aggro.
# - Next loop naturally checks aggro on the new tile.
#   - If aggro regained: Stay, reset counter to 0.
#   - If still no aggro: Increment counter, move to other tile again.
# - Full refresh ONLY after two consecutive moves without regaining aggro (full A→B→A cycle failed).
# - Full refresh: Prayer OFF, swoop attack closest crab, far west run, far east run back, prayer ON.
# - Aggro detection: Any 'aggressiveNpcs' list content = aggro.

import time
import random

# Core imports
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import player, inventory, npc_agro, slayer_task_remaining

# Utils imports
from modules.utils.click_tile import click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
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

# Aggro check: Any aggressiveNpcs list = aggro
def is_aggroed():
    agro_data = npc_agro()
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected (all tolerated).")
        return False
    else:
        print('agro detected')
        return True

# Constants
TILE_A = (1860, 3559)  # First local spot
TILE_B = (1868, 3556)  # Second local spot
FAR_WEST_TILE = (1836, 3561)
FAR_EAST_TILE = (1863, 3560)
RESET_RADIUS = 20
MINIMAP_ZOOM_FAR = 2.0
REAGGRO_WAIT_TICKS = 5  # ~12 seconds for crabs to wake after local reset

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting up camera...")
    camera(
        pitch=random.randint(300, 512),
        yaw=random.randint(600, 1000),
        zoom=random.randint(250, 300)
    )
    time.sleep(1)

    prayer_threshold = random.randint(15, 25)
    print(f"Initial prayer drink threshold: {prayer_threshold}")

    current_target = TILE_A
    failed_reset_count = 0
    print("Starting Sand Crabs script - local cycle until full A->B->A fails.")

    while True:
        # Check slayer task remaining
        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            break
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
            print("Aggro active - staying on current spot.")
            failed_reset_count = 0  # Regained aggro = success
        else:
            target_tuple = (current_target[0], current_target[1])
            print(f"No aggro - moving to local spot {target_tuple}")
            success = False
            for i in range(8):
                if click_tile(
                    current_target[0],
                    current_target[1],
                    action="Walk here",
                    tile_radius=RESET_RADIUS,
                    right_click=False,
                ):
                    wait_till_character_stopped_moving()
                    wait_for_next_tick(REAGGRO_WAIT_TICKS)  # Long wait for potential re-aggro
                    success = True
                    break
                wait_for_next_tick()
            if not success:
                print("Failed to click visible local spot after retries.")

            # Switch for next cycle
            current_target = TILE_B if current_target == TILE_A else TILE_A
            if not is_aggroed():
                failed_reset_count += 1

            # Full refresh only after full failed cycle (two moves, no aggro regained)
            if failed_reset_count >= 2:
                print("Full local cycle failed (A->B->A no aggro) - full refresh.")
                toggle_prayer('PROTECT_FROM_MELEE', activate=False)
                print("Prayer OFF for refresh.")

                print("Swoop: Attacking closest Sand Crab.")
                for _ in range(3):
                    if click_closest_npc('Sand Crab', option='Attack', max_attempts=3):
                        print("Swoop attack hit.")
                        wait_till_character_stopped_moving()
                        wait_for_next_tick(3)
                        break
                    wait_for_next_tick()

                print("Running far west.")
                click_minimap_tile(FAR_WEST_TILE[0], FAR_WEST_TILE[1], target_zoom=MINIMAP_ZOOM_FAR)
                wait_till_character_stopped_moving()
                wait_for_next_tick(2)

                print("Running back east.")
                click_minimap_tile(FAR_EAST_TILE[0], FAR_EAST_TILE[1], target_zoom=MINIMAP_ZOOM_FAR)
                wait_till_character_stopped_moving()
                wait_for_next_tick(3)

                toggle_prayer('PROTECT_FROM_MELEE', activate=True)
                print("Prayer ON after refresh.")

                failed_reset_count = 0
                current_target = TILE_A
                print("Refresh done - back to local cycle.")

        wait_for_next_tick(1)

if __name__ == "__main__":
    main()