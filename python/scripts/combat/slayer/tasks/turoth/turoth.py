# turoth.py
# Refactored using shared slayer utils (manage_prayer + get_slayer_task_remaining + hop utils)
# Special behavior preserved: mid-task bank via navigation reload, vial drop, high alch on rares,
# player hop check, endless swoop on Turoth only, protect melee

import sys
import time
import random
import importlib

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
from modules.utils.alch import high_alch_items
from modules.utils.inventory import is_inventory_full
from modules.utils.drop_item import drop_item

from scripts.combat.slayer.tasks.ankou.ankou import open_inventory
from scripts.combat.slayer.tasks.turoth.walk_to_turoth import run as run_navigation

# Shared utils
from scripts.combat.slayer.utils.slayer_task_utils import (
    check_if_need_for_hop,
    hop_until_empty,
    manage_prayer,
    get_slayer_task_remaining,
)

# Loot configuration
RARE_ITEMS = [
    "Mystic hat (dark)", "Mystic boots (dark)", "Leaf-bladed sword",
    "Mystic robe bottom (light)", "Adamant full helm", "Rune dagger"
]
COMMON_ITEMS = [
    "Death rune", "Nature rune", "Grimy ranarr weed",
    "Torstol seed", "Snape grass seed", "Cadantine seed", "Snapdragon seed", "Kwuarm seed"
]
LOOT_RADIUS = 15
SWOOP_MAX_ATTEMPTS = 100

def is_aggroed():
    """Only Turoth counts as aggro."""
    agro_data = npc_agro()
    aggressive_npcs = agro_data.get("aggressiveNpcs") if agro_data else []
    if any(npc.get("name") == "Turoth" for npc in aggressive_npcs):
        print("Aggro detected")
        return True
    else:
        print("No aggressive NPCs detected.")
        return False

def handle_full_inventory(max_vial_drops: int = 28) -> None:
    if not is_inventory_full():
        print("Inventory has space - no action needed")
        return

    print("Inventory full - attempting to make space by dropping vials")

    dropped_count = 0
    while is_inventory_full() and dropped_count < max_vial_drops:
        if drop_item("Vial"):
            dropped_count += 1
            print("Dropped vial #{} - space created".format(dropped_count))
            time.sleep(random.uniform(0.25, 0.55))
        else:
            print("No more vials found")
            break

    if not is_inventory_full():
        print("Space made by dropping {} vial(s)".format(dropped_count))
        return

    print("Inventory still full after vials - performing mid-task bank trip")
    try:
        run_navigation()
    except Exception as e:
        print("Mid-task navigation failed: {}".format(e))
        print("Stopping script - manual intervention required")
        sys.exit(1)

def loot_drops():
    handle_full_inventory()
    
    if has_ground_items(RARE_ITEMS, tile_radius=LOOT_RADIUS):
        print("Rare drop(s) detected - entering loot phase")
        for item in RARE_ITEMS + COMMON_ITEMS:
            if loot_all_ground_items(item):
                pass
    else:
        for item in COMMON_ITEMS:
            if loot_all_ground_items(item):
                pass

def swoop_reset():
    print("No aggro - starting swoop reset")
    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print("Swoop attempt {}".format(attempt + 1))
        if click_closest_npc("Turoth", option="Attack", max_attempts=5):
            print("Attacked Turoth - waiting for re-aggro")
            wait_till_character_stopped_moving(required_idle_ticks=3)
            while is_aggroed():
                wait_for_next_tick(1)
            print("Finished kill, short sleep")
            wait_for_next_tick(2)
            return True
        else:
            print("No Turoth in range")
    print("Swoop exhausted attempts")
    return False

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        sys.exit(1)

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting up camera...")
    camera(
        pitch=random.randint(334, 350),
        yaw=random.randint(200, 400),
        zoom=random.randint(260, 310)
    )

    prayer_threshold = random.randint(15, 25)
    print("Initial prayer threshold: {}".format(prayer_threshold))

    print("Starting Turoth slayer loop")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            print("Task completed!")
            break

        toggle_prayer("PROTECT_FROM_MELEE", activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        if is_aggroed():
            print("Aggro active - fighting")
        else:
            print("No aggro - loot then swoop")
            loot_drops()
            high_alch_items(RARE_ITEMS)
            if check_if_need_for_hop():
                hop_until_empty()
            swoop_reset()

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()