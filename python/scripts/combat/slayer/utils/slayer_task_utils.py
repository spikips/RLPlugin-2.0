import random
import time
import sys

from modules.core.window_utils import runelite_window
from modules.core.plugin_client import inventory, cannon_data, player, minimap_tile_point, slayer_task_remaining
from modules.core.mouse_control import move, right_click

from modules.utils.drop_item import drop_item
from modules.utils.inventory import is_inventory_full, click_inventory
from modules.utils.loot import has_ground_items, loot_all_ground_items, pickup_closest_ground_item
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.utils.check_players import check_for_players
from modules.utils.hop import hop_to_random_world
from modules.utils.check_if_in_tile import check_if_in_tile, click_tile
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.select_menu_option import select_menu_option

from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.cannon import click_cannon

from modules.object_data.object import get_closest_object

# Open inventory (general version using ankou's helper - works for most tasks)
from modules.widgets.widget import check_widget, click_widget, click_widget_child
# avoid circular import by using generic inventory opener
from modules.utils.drop_item import open_inventory_tab as open_inventory
# slayer_task_utils.py
# Reusable utilities for cannon-based Slayer tasks
# Single source of truth for cannon name
CANNON_NAME = "Dwarf multicannon"



def auto_retaliate(enable: bool):
    # open combat options tab
    if not click_widget('35913792', sprite_id=1026, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913792 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    if enable:
        check_auto_retaliate = check_widget("38862882", sprite_id=1141)
        if check_auto_retaliate:
            for i in range(5):
                if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
                    print('enabled auto retaliate')
                    break
                wait_for_next_tick()
                if i == 4:
                    exit("Failed to click dialogue option (auto retaliate) via child")
    else:
        check_auto_retaliate = check_widget("38862882", sprite_id=1150)
        if check_auto_retaliate:
            for i in range(5):
                if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
                    print('disabled auto retaliate')
                    break
                wait_for_next_tick()
                if i == 4:
                    exit("Failed to click dialogue option (auto retaliate) via child")
    # open inventory
    if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

def is_cannon_placed(cannon_tile: tuple, radius: int = 10) -> bool:
    fire_obj = get_closest_object(CANNON_NAME, "Fire", tile=cannon_tile, radius=radius)
    pickup_obj = get_closest_object(CANNON_NAME, "Pick-up", tile=cannon_tile, radius=radius)
    placed = fire_obj is not None or pickup_obj is not None
    print(f"CANNON CHECK: placed={placed}, fire={fire_obj is not None}, pickup={pickup_obj is not None}")
    return placed

def place_cannon(cannon_tile: tuple, cannon_base_item: str = "Cannon base") -> bool:
    # Move to tile
    while not check_if_in_tile(*cannon_tile, click=True):
        click_tile(cannon_tile[0], cannon_tile[1])
        wait_till_character_stopped_moving()

    if not click_inventory(cannon_base_item):
        print("No cannon base - assuming already placed")
        return True

    waited = 0
    while waited < 40:
        if get_closest_object(CANNON_NAME, "Fire", tile=cannon_tile, radius=10):
            print("Cannon placed")
            for _ in range(random.randint(2, 3)):
                click_cannon('Fire', exact_tile=cannon_tile)
            return True
        wait_for_next_tick(1)
        waited += 1
    print("Placement timeout")
    return False

def check_and_place_cannon(cannon_tile: tuple, cannon_base_item: str = "Cannon base"):
    for attempt in range(1, 11):
        # Try repair first
        if click_cannon('Repair', exact_tile=cannon_tile):
            print("Repairing cannon...")
            for _ in range(5):
                if is_cannon_placed(cannon_tile):
                    print("Cannon repaired")
                    break
                wait_for_next_tick(1)

        if place_cannon(cannon_tile, cannon_base_item):
            for _ in range(random.randint(2, 3)):
                click_cannon('Fire', exact_tile=cannon_tile)
                print("Cannon placed and loaded")
            auto_retaliate(enable=True)
            return
        print(f"Placement attempt {attempt}/10 failed")
        time.sleep(2)

def reload_cannon(current_threshold: int, cannon_tile: tuple):
    info = cannon_data().get('data', {})
    ammo = info.get('ammo', 0)

    if ammo > current_threshold:
        return None  # No change

    if click_cannon('Fire', exact_tile=cannon_tile):
        print(f"Reloaded cannon ({ammo} <= {current_threshold})")
        new_threshold = random.randint(5, 25)
        print(f"New reload threshold: {new_threshold}")
        wait_for_next_tick(1)
        return new_threshold

    # Try repair + reload
    if click_cannon('Repair', exact_tile=cannon_tile):
        print("Repairing then reloading...")
        for _ in range(10):
            if click_cannon('Fire', exact_tile=cannon_tile):
                new_threshold = random.randint(5, 25)
                print(f"Reloaded after repair - new threshold {new_threshold}")
                wait_for_next_tick(1)
                return new_threshold
            wait_for_next_tick(1)
    print("Failed to reload/repair")
    return None

def remove_cannon(cannon_tile: tuple):
    if is_cannon_placed(cannon_tile):
        if click_cannon('Pick-up', exact_tile=cannon_tile):
            while get_closest_object(CANNON_NAME, "Pick-up", tile=cannon_tile, radius=10):
                wait_for_next_tick(1)
            print("Cannon picked up")
        else:
            print("Failed to pick up cannon")

# Prayer
def check_prayer_level() -> int:
    data = player(prayer=True)
    return data['data'].get('prayer', 100) if data and 'data' in data else 100

def has_prayer_potion() -> bool:
    for item in inventory().get('data', []):
        if item.get('name', '').startswith('Prayer potion('):
            return True
    return False

def drink_prayer_potion() -> bool:
    # ensure inventory tab is open before checking contents
    open_inventory()
    inv = inventory(middle_point=True)
    if not inv or 'data' not in inv:
        return False
    for item in inv['data']:
        name = item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            mp = item.get('middle_point')
            if mp:
                sx, sy = runelite_window(mp['x'], mp['y'])
                move(sx, sy, fast=False, sleep=False, button='left')
                print(f"Drank {name}")
                wait_for_next_tick(1)
                return True
    return False

def manage_prayer(threshold: int) -> int | None:
    if check_prayer_level() <= threshold:
        if has_prayer_potion() and drink_prayer_potion():
            new_threshold = random.randint(15, 25)
            print(f"Potion drunk - new prayer threshold {new_threshold}")
            return new_threshold
        print("Prayer low, no potion")
    return None

# Inventory / Loot
def handle_full_inventory(max_vial_drops: int = 28, vial_item: str = 'Vial') -> bool:
    if not is_inventory_full():
        return True

    dropped = 0
    while is_inventory_full() and dropped < max_vial_drops:
        if drop_item(vial_item):
            dropped += 1
            time.sleep(random.uniform(0.25, 0.55))
        else:
            break

    if not is_inventory_full():
        print(f"Dropped {dropped} vials - space made")
        return True

    print("Still full after vials")
    return False  # Caller must bank

def loot_drops(rare_items: list, common_items: list, radius: int = 15) -> bool:
    looted = False

    if has_ground_items(rare_items, tile_radius=radius):
        print("Rare drop detected")
        for item in rare_items + common_items:
            handle_full_inventory()
            if pickup_closest_ground_item(item):
                looted = True
    else:
        for item in common_items:
            handle_full_inventory()
            if pickup_closest_ground_item(item):
                looted = True
    return looted

# Hopping
def check_if_need_for_hop(radius: int = 11) -> bool:
    if check_for_players(radius=radius, max_wait_ticks=2):
        print("Players detected - need hop")
        return True
    print("Area clear")
    return False

def hop_until_empty(radius: int = 11, max_hops: int = 20) -> bool:
    for _ in range(max_hops):
        if not check_if_need_for_hop(radius):
            return True
        hop_to_random_world('p2p')
        wait_for_tick(3)
    print("Failed to find empty world")
    return False

# Task
def get_slayer_task_remaining() -> int:
    return slayer_task_remaining()