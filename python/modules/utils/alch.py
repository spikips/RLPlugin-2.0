import random
import time
import re
import keyboard
from typing import List, Dict

from modules.banking.bank_castlewars import clean_item_name, get_inventory_data
from modules.core.plugin_client import inventory
from modules.core.window_utils import focus_runelite_window
from modules.widgets.widget import check_widget, click_widget
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.utils.inventory import click_inventory
from modules.widgets.widget import click_widget_by_name 


def get_widget_item_quantities(item_names: List[str]) -> Dict[str, int]:
    """Your provided function for accurate quantity parsing."""
    if not item_names:
        return {}

    normalized_to_original: Dict[str, str] = {}
    for orig in item_names:
        normalized_to_original[clean_item_name(orig)] = orig

    results: Dict[str, int] = {orig: 0 for orig in item_names}

    inv = get_inventory_data()
    if not inv:
        return results

    for entry in inv:
        raw_name = entry.get('name', '')
        if not raw_name:
            continue
        base = clean_item_name(raw_name)
        qty = int(entry.get('quantity', 1) or 1)

        if base in normalized_to_original:
            orig = normalized_to_original[base]
            results[orig] += qty

    return results


def open_magic_spellbook() -> bool:
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    widget_id = '35913798'
    if check_widget(widget_id, sprite_id=-1):
        print("Magic spellbook not open, attempting to open it.")
        for _ in range(3):
            click_widget(widget_id, sprite_id=1027, rand_x=10, rand_y=10)
            for _ in range(60):
                if not check_widget(widget_id, sprite_id=-1):
                    print("Magic spellbook opened.")
                    return True
                time.sleep(0.01)
    else:
        print("Magic spellbook already open.")
        return True
    print("Failed to open magic spellbook.")
    return False


def open_inventory_tab() -> bool:
    if not focus_runelite_window():
        return False

    widget_id = '35913795'
    if check_widget(widget_id, sprite_id=-1):
        print("Inventory not open, attempting to open it.")
        for _ in range(3):
            click_widget(widget_id, sprite_id=1030, rand_x=20, rand_y=20)
            for _ in range(60):
                inv_data = inventory()
                if inv_data and 'data' in inv_data:
                    return True
                time.sleep(0.01)
    else:
        return True
    return False


def high_alch_items(items: List[str]) -> int:
    """
    Calculates maximum possible alchs ONCE at the start (based on items + runes),
    builds a fixed sequence, then alchs exactly that many times.
    No repeated quantity checks or inventory opens for checking (only for clicking).
    """
    if not items:
        print("No items provided.")
        return 0

    # One-time accurate quantity check
    if not open_inventory_tab():
        print("Failed to open inventory for initial check.")
        return 0

    query_items = items + ['Nature rune', 'Fire rune']
    quantities = get_widget_item_quantities(query_items)

    total_target_items = sum(quantities.get(item, 0) for item in items)
    nature_qty = quantities.get('Nature rune', 0)
    fire_qty = quantities.get('Fire rune', 0)

    max_from_nature = nature_qty  # 1 per alch
    max_from_fire = fire_qty // 5
    max_alchs = min(total_target_items, max_from_nature, max_from_fire)

    if max_alchs == 0:
        if total_target_items == 0:
            print("No target items found in inventory.")
        elif nature_qty < 1:
            print(f"Insufficient nature runes (have {nature_qty}, need at least 1 per alch).")
        else:
            print(f"Insufficient fire runes (have {fire_qty}, need at least 5 per alch).")
        return 0

    print(f"Initial check complete: Can alch up to {max_alchs} items "
          f"({total_target_items} target items, {nature_qty} natures, {fire_qty} fires).")

    # Build fixed alch sequence in the order of the provided list
    alch_sequence: List[str] = []
    for item in items:
        count = quantities.get(item, 0)
        # Only add up to the remaining allowed alchs
        add_count = min(count, max_alchs - len(alch_sequence))
        alch_sequence.extend([item] * add_count)
        if len(alch_sequence) >= max_alchs:
            break

    total_alched = 0
    for i, current_item in enumerate(alch_sequence, 1):
        if not open_magic_spellbook():
            print("Failed to open magic spellbook.")
            break

        if not click_widget_by_name('High Level Alchemy', action='Cast'):
            print("Failed to select High Level Alchemy spell.")
            break

        time.sleep(0.1)

        if not open_inventory_tab():
            break

        if not click_inventory(current_item):
            print(f"Failed to find/click {current_item} (attempt {i}). Stopping early.")
            break

        print(f"Alched {current_item} ({i}/{len(alch_sequence)})")

        wait_for_next_tick(5)

        total_alched += 1

    print(f"Finished alching. Total successful alchs: {total_alched} (planned: {len(alch_sequence)})")
    
    keyboard.press_and_release('f1')
    return total_alched


# Example usage
# time.sleep(1)
# items_to_alch = ['adamant 2h sword', 'adamant battleaxe', 'rune scimitar']
# high_alch_items(items_to_alch)