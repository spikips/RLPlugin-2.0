# sand_crabs.py
# Refactored like kalphites.py: uses shared slayer utils (prayer + task check)
# 100 percent same behavior: local A/B tile cycle, full refresh only after 2 failed resets (swoop + far west/east run), aggro detection
# Bigger picture: prayer logic now lives in one file - fix/update once and every slayer task (cannon or non-cannon) instantly improves. Less bugs, faster maintenance.

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import npc_agro

# Utils
from modules.utils.click_tile import click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.camera import camera

# Shared utils (the efficiency win)
from scripts.combat.slayer.utils.slayer_task_utils import (
    manage_prayer,
    get_slayer_task_remaining,
)

def is_aggroed():
    """Exact original aggro check."""
    agro_data = npc_agro()
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected (all tolerated).")
        return False
    else:
        print('agro detected')
        return True

# Constants
TILE_A = (1860, 3559)
TILE_B = (1868, 3556)
FAR_WEST_TILE = (1836, 3561)
FAR_EAST_TILE = (1863, 3560)
RESET_RADIUS = 20
MINIMAP_ZOOM_FAR = 2.0
REAGGRO_WAIT_TICKS = 5

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return

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
    print("Initial prayer threshold: {}".format(prayer_threshold))

    current_target = TILE_A
    failed_reset_count = 0
    print("Sand Crabs script started - local A/B cycle.")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            break

        toggle_prayer('PROTECT_FROM_MELEE', activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p
            
        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        if is_aggroed():
            print("Aggro active - staying put.")
            failed_reset_count = 0
        else:
            print("No aggro - moving to local spot {}".format(current_target))
            success = False
            for i in range(8):
                if click_tile(current_target[0], current_target[1], action="Walk here", tile_radius=RESET_RADIUS, right_click=False):
                    wait_till_character_stopped_moving()
                    wait_for_next_tick(REAGGRO_WAIT_TICKS)
                    success = True
                    break
                wait_for_next_tick()
            if not success:
                print("Failed to click local spot after retries.")

            current_target = TILE_B if current_target == TILE_A else TILE_A

            if not is_aggroed():
                failed_reset_count += 1

            if failed_reset_count >= 2:
                print("Full cycle failed - full refresh.")
                toggle_prayer('PROTECT_FROM_MELEE', activate=False)

                print("Swoop attack on closest Sand Crab.")
                for _ in range(3):
                    if click_closest_npc('Sand Crab', option='Attack', max_attempts=3):
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
                failed_reset_count = 0
                current_target = TILE_A
                print("Refresh done - back to local cycle.")

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()