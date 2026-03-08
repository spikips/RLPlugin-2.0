# ogres.py
# Refactored using shared slayer utils
# Special behavior preserved: prayer OFF by default, only ON during rare loot phase + camera zoom change

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window

# Player
from modules.player_data.prayer.toggle_prayer import toggle_prayer

# Utils
from modules.utils.camera import camera
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.loot import has_ground_items, loot_all_ground_items
from modules.utils.wait_for_tick import wait_for_next_tick

# Shared utils
from scripts.combat.slayer.utils.slayer_task_utils import (
    is_cannon_placed,
    check_and_place_cannon,
    reload_cannon,
    remove_cannon,
    get_slayer_task_remaining,
)

# Constants
CANNON_TILE = (2494, 3098, 0)
STAND_TILE  = (2492, 3097, 0)
LOOT_ITEMS = [
    "loop half of key", "tooth half of key", "rune spear", "shield left half",
    "dragon spear", "long bone", "Curved Bone", "snapdragon seed",
    "torstol seed", "ranarr seed", "snape grass seed"
]
LOOT_RADIUS = 10

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite.")
        return

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    prayer_threshold = random.randint(15, 25)
    cannon_threshold = random.randint(5, 25)
    print("Initial thresholds - Prayer: {} Cannon: {}".format(
        prayer_threshold, cannon_threshold))

    print("Ogre cannon task started (prayer only during loot).")

    while True:
        if get_slayer_task_remaining() == 0:
            remove_cannon(CANNON_TILE)
            print("Task complete - cannon picked up.")
            break

        if not is_cannon_placed(CANNON_TILE):
            check_and_place_cannon(CANNON_TILE)

        new_c = reload_cannon(cannon_threshold, CANNON_TILE)
        if new_c is not None:
            cannon_threshold = new_c

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        # Loot phase (rare triggered)
        if random.randint(0, 100) < 10:
            if has_ground_items(LOOT_ITEMS, tile_radius=LOOT_RADIUS):
                toggle_prayer('PROTECT_FROM_MELEE', activate=True)
                print("Rare drops detected - Prayer ON + low zoom")
                camera(
                    pitch=random.randint(450, 512),
                    yaw=random.randint(1100, 1400),
                    zoom=200
                )

                for item in LOOT_ITEMS:
                    loot_all_ground_items(item, tile_radius=10)

                check_if_in_tile(*STAND_TILE, click=True)

                toggle_prayer('PROTECT_FROM_MELEE', activate=False)
                print("Loot complete - Prayer OFF")
                camera(
                    pitch=random.randint(450, 512),
                    yaw=random.randint(1100, 1400),
                    zoom=1000
                )
            else:
                print("No rare drops - prayer remains OFF")

            wait_for_next_tick(1)
    
def run():
    main()

if __name__ == "__main__":
    run()