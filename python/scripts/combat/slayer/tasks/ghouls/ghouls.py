# ghoul.py
# Refactored like kalphites.py & sand_crabs.py: uses shared slayer utils
# 100 percent same behavior: cannon at (3427, 3461, 0), no fixed stand tile, no looting,
# random camera, dynamic thresholds, pick-up on task end, protect melee
# Bigger picture: prayer + cannon logic centralized → one change improves every cannon task instantly

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.core.plugin_client import inventory

# Player
from modules.player_data.prayer.toggle_prayer import toggle_prayer

# Utils
from modules.utils.camera import camera
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick

# Shared utils (efficiency win)
from scripts.combat.slayer.utils.slayer_task_utils import (
    is_cannon_placed,
    check_and_place_cannon,
    reload_cannon,
    remove_cannon,
    manage_prayer,
    get_slayer_task_remaining,
)

# Constants
CANNON_TILE = (3427, 3461, 0)
CANNON_NAME = "Dwarf multicannon"  # already in utils, but kept for clarity

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite.")
        return

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting random camera...")
    camera(
        pitch=random.randint(420, 512),
        yaw=random.randint(150, 500),
        zoom=random.randint(500, 700)
    )
    time.sleep(1)

    prayer_threshold = random.randint(15, 25)
    cannon_threshold = random.randint(5, 25)
    print("Initial thresholds - Prayer: {} Cannon: {}".format(prayer_threshold, cannon_threshold))

    print("Ghoul cannon task started (no fixed stand tile, no loot).")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            remove_cannon(CANNON_TILE)
            print("Task complete - cannon picked up. Script ends (restart for new task).")
            break

        # Cannon management (repair/place/load/auto-retaliate via shared func)
        if not is_cannon_placed(CANNON_TILE):
            check_and_place_cannon(CANNON_TILE)

        # Prayer (shared logic)
        toggle_prayer('PROTECT_FROM_MELEE', activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        # Cannon reload (shared logic)
        new_c = reload_cannon(cannon_threshold, CANNON_TILE)
        if new_c is not None:
            cannon_threshold = new_c


        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()