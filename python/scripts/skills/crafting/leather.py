import sys
import random
import time
import re
import keyboard
from collections import Counter

from modules.core.plugin_client import bank_items, inventory
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.banking import bank
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.core.window_utils import focus_runelite_window
from modules.utils.inventory import click_inventory
from modules.widgets.widget import click_widget_by_name
from modules.player_data.get_level import get_level


def clean_item_name(name: str) -> str:
    return re.sub(r'\s*\(\d+\)$', '', name or '').strip().lower()


def is_bank_open() -> bool:
    return len(bank_items().get('data', [])) > 0


def close_bank():
    keyboard.press('esc')
    time.sleep(random.uniform(0.05, 0.1))
    keyboard.release('esc')
    wait_for_next_tick()


def get_current_inventory_dict() -> dict:
    inv = inventory().get('data', [])
    counter = Counter()
    for item in inv:
        raw = item.get('name', '')
        if raw:
            base = clean_item_name(raw)
            counter[base] += item.get('quantity', 1)
    return dict(counter)


def bank_leather(leather_type: str = "leather"):
    focus_runelite_window()
    target_inventory = {
        "needle": 1,
        "thread": "all",
        leather_type: "all"
    }
    current = get_current_inventory_dict()
    target_bases = {clean_item_name(k) for k in target_inventory}
    is_perfect = True
    for k, v in target_inventory.items():
        base = clean_item_name(k)
        qty = current.get(base, 0)
        if isinstance(v, int):
            if qty < v:
                is_perfect = False
                break
        else:
            if qty == 0:
                is_perfect = False
                break
    if is_perfect and not any(b not in target_bases for b in current):
        print("Inventory already perfect - skipping bank")
        if is_bank_open():
            close_bank()
        return
    if not is_bank_open():
        print("Opening bank via closest Banker NPC...")
        for i in range(10):
            if not click_closest_npc('banker', option='bank', max_attempts=5):
                wait_for_next_tick()
            else:
                if wait_till_character_stopped_moving(required_idle_ticks=1):
                    break
            if i == 9:
                sys.exit("Failed to click npc (banker)")
        wait_for_next_tick(1)
    print("Depositing only junk items...")
    for base in list(current.keys()):
        if base not in target_bases:
            print("  -> Depositing all " + base)
            bank(deposit=base, quantity="all")
            wait_for_next_tick()
    print("Topping up missing items...")
    for name, qty in target_inventory.items():
        base = clean_item_name(name)
        curr = get_current_inventory_dict().get(base, 0)
        if isinstance(qty, int) and curr < qty:
            need = qty - curr
            print("  -> Withdrawing " + str(need) + " " + name)
            bank(withdraw=name, quantity=str(need))
        elif qty == "all" and curr == 0:
            print("  -> Withdrawing all " + name)
            bank(withdraw=name, quantity="all")
        wait_for_next_tick(1)
    close_bank()
    print("Banking complete (" + leather_type + ") - ready to craft!")


def get_craft_target(current_level: int) -> str:
    targets = {
        1: "leather gloves",
        7: "leather boots",
        9: "leather cowl",
        11: "leather vambraces",
        14: "leather body",
        18: "leather chaps"
    }
    for req in sorted(targets.keys(), reverse=True):
        if current_level >= req:
            return targets[req]
    return "leather gloves"


def craft_leather():
    focus_runelite_window()
    leather_type = "leather"
    while True:
        lvl = get_level("Crafting")
        if lvl < 1:
            print("Crafting level too low (<1) - stopping")
            break
        elif lvl >= 20:
            return True
        current = get_current_inventory_dict()
        leather_left = current.get(leather_type, 0)
        if leather_left == 0:
            print("No leather left - re-banking...")
            bank_leather(leather_type)
            continue
        item_to_make = get_craft_target(lvl)
        print("Starting batch: " + item_to_make + " (level " + str(lvl) + ", " + str(leather_left) + " leather left)")
        for i in range(5):
            if click_inventory('needle', action='use', hover_only=False):
                break
            wait_for_next_tick()
            if i == 4:
                sys.exit("Failed to click inventory item (Needle, Use)")
        for i in range(5):
            if click_inventory(leather_type, action='use', hover_only=False):
                break
            wait_for_next_tick()
            if i == 4:
                sys.exit("Failed to click inventory item (Leather, Use)")
        for i in range(5):
            if click_widget_by_name(item_to_make, action='make', canvas=(0, 341, 514, 141)):
                break
            wait_for_next_tick()
            if i == 4:
                sys.exit("Failed to click widget (" + item_to_make + ", Make)")
        print("  -> Batch started, waiting until finished...")
        while True:
            wait_for_next_tick()
            new_leather_left = get_current_inventory_dict().get(leather_type, 0)
            if new_leather_left == 0:
                print("  -> Batch complete! " + str(leather_left - new_leather_left) + " leather used.")
                break
            new_lvl = get_level("Crafting")
            if new_lvl > lvl:
                new_target = get_craft_target(new_lvl)
                if new_target != item_to_make:
                    print("  -> Level up! Switching to " + new_target + " (better item available)")
                    break
            elif new_lvl >= 20:
                print("  -> Reached level 20 - stopping crafting")
                return True
        


if __name__ == "__main__":
    craft_leather()