# check_inventory_and_equipment.py
# (or banking.py – rename as needed)
# Full banking helper script with smart gear & inventory setup
# Prefers highest charges/doses when withdrawing, skips 0-charge jewelry/potions
# Deposits extras lowest charge first

import time
import random
import re
from collections import Counter

from modules.core.plugin_client import gear, inventory, interact_options, bank_items
from modules.core.mouse_control import move, scroll
from modules.core.window_utils import runelite_window
from modules.utils.banking import bank
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick


# Items that have charges/doses – prefer highest, skip 0-charge where applicable
CHARGEABLE_ITEMS = {
    "Amulet of glory",
    "Combat bracelet",
    "Ring of wealth",
    "Games necklace",
    "Ring of dueling",
    "Skills necklace",
    "Necklace of passage",   # Added as requested
    "Prayer potion",
    "Antidote++",
    # Add more as needed (e.g. "Stamina potion", "Super restore")
}
import re
from collections import Counter

def clean_item_name(name: str) -> str:
    """Remove trailing charge/dose indicator like ' (5)' or '(6)' from item name."""
    if not name:
        return ''
    # Handles both 'Item (5)' and 'Item(5)'
    return re.sub(r'\s*\(\d+\)$', '', name).strip()


# Gear helpers
def get_current_gear_set() -> set[str]:
    """Returns a set of cleaned equipped item names."""
    gear_raw = gear().get('data', {})
    return {clean_item_name(name) for name in gear_raw.keys() if name}

# Inventory-specific helpers
def get_current_inventory_dict() -> dict[str, int]:
    """Returns dict of cleaned inventory item names → total quantity."""
    inv_raw = inventory().get('data', [])
    counter = Counter()
    for item in inv_raw:
        clean = clean_item_name(item.get('name', ''))
        if clean:
            qty = item.get('quantity', 1)
            counter[clean] += qty
    return dict(counter)

def get_current_gear_list() -> list[str]:
    """Returns sorted list of cleaned equipped item names."""
    gear_raw = gear().get('data', {})
    return sorted(clean_item_name(name) for name in gear_raw.keys() if name)

def check_inventory_and_equipment() -> None:
    """
    Prints current gear & inventory in Python code format.
    Ready to copy-paste as target_gear and target_inventory for is_correct_setup().
    """
    current_gear = get_current_gear_list()
    current_inv = get_current_inventory_dict()

    # Gear list
    gear_lines = ",\n    ".join(f'"{item}"' for item in current_gear)
    print("target_gear = [")
    if gear_lines:
        print(f"    {gear_lines}")
    print("]\n")

    # Inventory dict
    print("target_inventory = {")
    for name, count in current_inv.items():
        print(f'    "{name}": {count},')
    if current_inv:
        print("}")  # Closes dict if not empty
    else:
        print("}")  # Empty dict

# Example targets and test calls (bank must be open)
# target_gear = [
#     "Amulet of glory",
#     "Ancient cloak",
#     "Ancient mitre",
#     "Antler guard",
#     "Brine sabre",
#     "Climbing boots",
#     "Combat bracelet",
#     "Honourable blessing",
#     "Monk's robe",
#     "Monk's robe top",
#     "Ring of wealth"
# ]

# target_inventory = {
#     "Amulet of glory": 1,
#     "Games necklace": 1,
#     "Prayer potion": 5,
#     "Ring of dueling": 2,
# }


target_gear = [
    "Amulet of glory",
    "Ancient cloak",
    "Ancient mitre",
    "Antler guard",
    "Brine sabre",
    "Climbing boots",
    "Combat bracelet",
    "Honourable blessing",
    "Monk's robe",
    "Monk's robe top",
    "Ring of wealth"
]

target_inventory = {
    "Prayer potion": 2,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Cannon barrels": 1,
    "Cannon furnace": 1,
    "Cannon base": 1,
    "Cannon stand": 1,
    "Steel cannonball": "all",
}




check_inventory_and_equipment()