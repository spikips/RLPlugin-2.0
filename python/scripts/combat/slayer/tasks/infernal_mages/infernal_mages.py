# infernal_mages.py
# Refactored using shared slayer utils (same clean style as ankou/shade)
# Same behavior: protect from magic, dynamic prayer, loot rares trigger full loot,
# endless swoop on Infernal Mage only, random camera, task end break

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import npc_agro

# Utils
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.camera import camera
from modules.utils.loot import has_ground_items, loot_all_ground_items

# Shared utils
from scripts.combat.slayer.utils.slayer_task_utils import (
    manage_prayer,
    get_slayer_task_remaining,
)

# Constants
RARE_ITEMS = ["Mystic hat (dark)", "Mystic boots (dark)"]
COMMON_ITEMS = ["Death rune"]
LOOT_RADIUS = 10
SWOOP_MAX_ATTEMPTS = 100

def is_aggroed():
    """Only Infernal Mage counts as aggro."""
    agro_data = npc_agro()
    aggressive_npcs = agro_data.get("aggressiveNpcs") if agro_data else []
    if any(npc.get("name") == "Infernal Mage" for npc in aggressive_npcs):
        print("Aggro detected")
        return True
    else:
        print("No aggressive NPCs detected.")
        return False

def loot_drops():
    """Rare-triggered loot (original logic)."""
    if has_ground_items(RARE_ITEMS, tile_radius=LOOT_RADIUS):
        print("Rare drop(s) detected - entering loot phase")
        for item in RARE_ITEMS + COMMON_ITEMS:
            if loot_all_ground_items(item):
                pass
    else:
        for item in COMMON_ITEMS:
            if loot_all_ground_items(item):
                pass
    return False

def swoop_reset():
    """Exact endless swoop on Infernal Mage."""
    print("No aggro - starting swoop reset (attacking closest Infernal Mage)")
    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print("Swoop attempt {}".format(attempt + 1))
        if click_closest_npc("Infernal Mage", option="Attack", max_attempts=5):
            print("Infernal Mage attacked - waiting for re-aggro")
            wait_till_character_stopped_moving(required_idle_ticks=3)
            while is_aggroed():
                wait_for_next_tick(1)
            else:
                print("finished kill, sleeping for 2 ticks")
                wait_for_next_tick(2)
                return True
        else:
            print("No Infernal Mage in range for swoop")
    print("Swoop exhausted max attempts")
    return False

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite.")
        return

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting random camera...")
    camera(
        pitch=random.randint(334, 350),
        yaw=random.randint(200, 400),
        zoom=random.randint(260, 310)
    )

    prayer_threshold = random.randint(15, 25)
    print("Initial prayer threshold: {}".format(prayer_threshold))

    print("Infernal Mage slayer task started.")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            print("Task complete - script ending.")
            break

        toggle_prayer("PROTECT_FROM_MAGIC", activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        if is_aggroed():
            print("Aggro active - fighting normally.")
        else:
            print("No aggro - looting drops first.")
            swoop_reset()
            loot_drops()

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()