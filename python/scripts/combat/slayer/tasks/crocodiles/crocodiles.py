# crocodile.py
# Refactored using shared slayer utils (same as kalphites/vampyre/ghoul etc)
# Same behavior: cannon at (3191,2825,0), stand at (3191,2823,0), random camera,
# protect melee, dynamic thresholds, looting Grimy ranarr weed, pick-up on task end

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window

# Player
from modules.player_data.prayer.toggle_prayer import toggle_prayer

# Utils
from modules.utils.camera import camera
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.loot import loot_all_ground_items
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving

# Shared utils (centralized cannon + prayer)
from scripts.combat.slayer.utils.slayer_task_utils import (
    is_cannon_placed,
    check_and_place_cannon,
    reload_cannon,
    remove_cannon,
    manage_prayer,
    get_slayer_task_remaining,
)

# Constants
CANNON_TILE = (3191, 2825, 0)
STAND_TILE  = (3191, 2823, 0)
LOOT_ITEMS = ["Grimy ranarr weed"]
LOOT_RADIUS = 15

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite.")
        return

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting random camera...")
    camera(
        pitch=random.randint(300, 512),
        yaw=random.randint(600, 1000),
        zoom=random.randint(250, 300)
    )

    prayer_threshold = random.randint(15, 25)
    cannon_threshold = random.randint(5, 25)
    print("Initial thresholds - Prayer: {} Cannon: {}".format(
        prayer_threshold, cannon_threshold))

    print("Crocodile cannon task started.")

    while True:
        if get_slayer_task_remaining() == 0:
            remove_cannon(CANNON_TILE)
            print("Task complete - cannon picked up.")
            break

        if not is_cannon_placed(CANNON_TILE):
            check_and_place_cannon(CANNON_TILE)

        if not check_if_in_tile(*STAND_TILE, click=True):
            click_minimap_tile(STAND_TILE[0], STAND_TILE[1], target_zoom=5.0)
            wait_till_character_stopped_moving()

        toggle_prayer('PROTECT_FROM_MELEE', activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        new_c = reload_cannon(cannon_threshold, CANNON_TILE)
        if new_c is not None:
            cannon_threshold = new_c

        # Loot
        if random.randint(0, 100) < 10:
            for item in LOOT_ITEMS:
                count = loot_all_ground_items(item, tile_radius=LOOT_RADIUS, delay_range=(0.2, 0.5))
                if count > 0:
                    print("Looted {}x {}".format(count, item))

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()