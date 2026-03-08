# aberrant_spectres.py

import sys
import random

from modules.core.window_utils import focus_runelite_window
from modules.utils.camera import camera
from modules.utils.alch import high_alch_items
from modules.player_data.prayer.toggle_prayer import toggle_prayer

from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.inventory import check_inventory_space
from scripts.combat.slayer.utils.slayer_task_utils import (
    auto_retaliate,
    is_cannon_placed,
    check_and_place_cannon,
    reload_cannon,
    remove_cannon,
    manage_prayer,
    handle_full_inventory,
    loot_drops,
    get_slayer_task_remaining,
    check_if_need_for_hop,
    hop_until_empty
)

from scripts.combat.slayer.tasks.aberrant_spectres.walk_to_aberrant_spectres import bank


# Loot
ALCH_ITEMS = RARE_ITEMS = [
    'Mystic robe bottom (dark)', 'Lava battlestaff', 'Rune full helm',
    'Adamant platebody', 'Rune kiteshield', 'Dragon spear'
]
COMMON_ITEMS = [
    'Grimy ranarr weed', 'Grimy irit leaf', 'Grimy avantoe', 'Grimy kwuarm',
    'Grimy cadantine', 'Grimy lantadyme', 'Grimy dwarf weed',
    'Torstol seed', 'Snapdragon seed', 'Ranarr seed', 'Lantadyme seed'
]
LOOT_RADIUS = 8

# Cannon setup - only tile and base item needed now
CANNON_TILE = (2469, 9776, 0)

# Movement helpers for stand tile
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.wait_for_tick import wait_for_next_tick

def main():
    if not focus_runelite_window():
        sys.exit("Failed to focus window")

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    camera(pitch=random.randint(334, 350), yaw=random.randint(200, 400), zoom=random.randint(260, 310))

    prayer_threshold = random.randint(15, 25)
    cannon_threshold = random.randint(5, 25)

    print("Starting Aberrant Spectres with cannon")

    while True:
        if get_slayer_task_remaining() == 0:
            print("Task completed!")
            
            # check if enough inventory space to pickup cannon, else bank and then pickup
            if check_inventory_space() >= 24:
                bank()
            remove_cannon(CANNON_TILE)
            break

        # Cannon
        if not is_cannon_placed(CANNON_TILE):
            check_and_place_cannon(CANNON_TILE)

        new_thresh = reload_cannon(cannon_threshold, CANNON_TILE)
        if new_thresh is not None:
            cannon_threshold = new_thresh


        # Prayer
        new_thresh = manage_prayer(prayer_threshold)
        if new_thresh is not None:
            prayer_threshold = new_thresh

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        toggle_prayer('PROTECT_FROM_MAGIC', activate=True)

        # Inventory / loot
        if not handle_full_inventory():
            print("Inventory still full - banking")
            toggle_prayer('PROTECT_FROM_MAGIC', activate=False)
            bank()
            toggle_prayer('PROTECT_FROM_MAGIC', activate=True)

        if random.randint(0, 100) < 10:
            looted = loot_drops(RARE_ITEMS, COMMON_ITEMS, LOOT_RADIUS)
            if looted:
                high_alch_items(ALCH_ITEMS)

        # Hop if needed
        if check_if_need_for_hop(radius=6):
            auto_retaliate(enable=False)
            remove_cannon(CANNON_TILE)
            hop_until_empty()
            auto_retaliate(enable=True)

        wait_for_next_tick(1)

def run():
    main()

if __name__ == "__main__":
    run()