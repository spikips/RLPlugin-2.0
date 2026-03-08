import sys
import random
import time
import re
import keyboard
from collections import Counter

from modules.core.plugin_client import bank_items, inventory, stats as plugin_stats
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.banking import bank
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.core.window_utils import focus_runelite_window
from modules.utils.inventory import click_inventory
from modules.utils.logout import logout_and_break
from modules.widgets.widget import check_widget


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


def bank_sapphire():
    focus_runelite_window()
    target_inventory = {
        "chisel": 1,
        "uncut sapphire": "all"
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
        print("Inventory already perfect for sapphire cutting - skipping bank")
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
            if not bank(withdraw=name, quantity="all"):
                sys.exit(f"Failed to withdraw {name} from bank")
        wait_for_next_tick(1)

    close_bank()
    print("Banking complete - ready to cut sapphires!")


def cut_sapphires(allow_break=True):
    focus_runelite_window()
    time.sleep(2)

    crafting_level = plugin_stats().get('data', {}).get('Crafting', {}).get('level', 0)
    print(f"Starting sapphire cutting at level {crafting_level}")

    while True:
        current = get_current_inventory_dict()
        uncut_left = current.get("uncut sapphire", 0)
        if uncut_left == 0:
            print("No uncut sapphires left - re-banking...")
            bank_sapphire()
            continue

        print(f"Crafting sapphires... ({uncut_left} uncut left)")

        for i in range(5):
            if click_inventory('chisel', action='use', hover_only=False):
                break
            wait_for_next_tick()
            if i == 4:
                sys.exit("Failed to click chisel")
        for i in range(5):
            if click_inventory('uncut sapphire', action='use', hover_only=False):
                break
            wait_for_next_tick()
            if i == 4:
                sys.exit("Failed to click uncut sapphire")

        for i in range(5):
            if check_widget('17694735'):
                break
            wait_for_next_tick()
            if i == 4:
                exit("Failed to click inventory item (Uncut sapphire, Cut)")

        keyboard.press_and_release("space")
        print("Pressed Space - Make All started")

        print("  -> Waiting for batch to finish...")
        while True:
            wait_for_next_tick()
            new_uncut = get_current_inventory_dict().get("uncut sapphire", 0)
            if new_uncut == 0:
                print(f"  -> Batch complete! Crafted {uncut_left - new_uncut} sapphires.")
                break

        if allow_break:
            if random.random() < 0.13:
                sleep_time = random.uniform(12, 90)
                print(f"Short break ({sleep_time:.1f}s)")
                time.sleep(sleep_time)
            if random.random() < 0.009:
                break_time = random.uniform(1800, 5400)
                print(f"Long break ({break_time/60:.1f} min)")
                logout_and_break(int(break_time))


if __name__ == "__main__":
    cut_sapphires(allow_break=False)