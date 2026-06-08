# ankou.py
# Refactored using shared slayer utils (same clean style as sand_crabs/shade)
# Same behavior: protect melee, dynamic prayer, endless swoop on no aggro,
# rare-triggered loot, random camera, task end break

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import inventory, npc_agro

# Utils
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.camera import camera
from modules.utils.loot import has_ground_items, loot_all_ground_items

# Shared utils
from modules.widgets.widget import check_widget, click_widget
from scripts.combat.slayer.utils.slayer_task_utils import (
    manage_prayer,
    get_slayer_task_remaining,
)

# Constants
LOOT_ITEMS = [
    "Blood rune", "Ranarr seed", "Snape grass seed", "Snapdragon seed",
    "Torstol seed", "Dragon spear", "Shield left half", "Rune spear",
    "Loop half of key", "Tooth half of key", "ancient shard",
    "Dark totem base", "Dark totem middle", "Dark totem top",
    "Grimy ranarr weed"
]
SWOOP_MAX_ATTEMPTS = 100

def open_inventory():
    inv_data = check_widget('35913795', sprite_id=-1)
    if inv_data:
        print("Inventory not open, attempting to open it.")
        for _ in range(3):
            click_widget('35913795', sprite_id=1030, rand_x=10, rand_y=10)

            for _ in range(60):
                inv_data = inventory()
                if inv_data and 'data' in inv_data:
                    break
                time.sleep(0.01)

def is_aggroed():
    """Exact original aggro check."""
    agro_data = npc_agro()
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected.")
        return False
    else:
        print("agro detected")
        return True


def swoop_reset():
    """Exact endless swoop on Ankou until aggro back."""
    print("No aggro - starting swoop reset (attacking closest Ankou)")
    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print("Swoop attempt {}".format(attempt + 1))
        if click_closest_npc("Ankou", option="Attack", max_attempts=5):
            print("Ankou attacked - waiting for re-aggro")
            wait_till_character_stopped_moving()
            wait_for_next_tick(10)
            while is_aggroed():
                wait_for_next_tick(1)
            else:
                print("finished kill, sleeping for 3 ticks")
                wait_for_next_tick(3)
                return True
        else:
            print("No Ankou in range for swoop")
        wait_for_next_tick(3)
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
        pitch=random.randint(300, 512),
        yaw=random.randint(600, 1000),
        zoom=random.randint(420, 500)
    )
    time.sleep(1)

    prayer_threshold = random.randint(15, 25)
    print("Initial prayer threshold: {}".format(prayer_threshold))

    print("Ankou slayer task started.")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            print("Task complete - script ending.")
            break

        toggle_prayer("PROTECT_FROM_MELEE", activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p


        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)
            
        if random.randint(0, 100) < 10:
            for item in LOOT_ITEMS:
                count = loot_all_ground_items(item, tile_radius=10, delay_range=(0.2, 0.5))
                if count > 0:
                    print("Looted {}x {}".format(count, item))

        if is_aggroed():
            print("Aggro active - fighting normally.")
        else:
            swoop_reset()

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()