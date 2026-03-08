import time
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.utils.inventory import click_inventory
from modules.widgets.widget import click_widget_by_name, click_widget
from modules.core.plugin_client import inventory
import random
from datetime import datetime
from datetime import timedelta
from modules.utils.logout import logout_and_break


def take_humanlike_break_if_needed(script_start_time: float, next_break_minutes: list) -> bool:
    elapsed_minutes = (time.time() - script_start_time) / 60
    if elapsed_minutes >= next_break_minutes[0]:
        sleep_minutes = round(random.triangular(10, 60, 25))
        wake_up_time = datetime.now() + timedelta(minutes=sleep_minutes)
        next_cycle_minutes = round(random.triangular(25, 95, 55))
        print("\n" + "="*65)
        print("TAKING HUMANLIKE BREAK")
        print(f"Sleep duration     : {sleep_minutes} minutes")
        print(f"Will log back in at: {wake_up_time.strftime('%H:%M:%S')}")
        print(f"Next cycle length  : ~{next_cycle_minutes} minutes")
        print("="*65 + "\n")
        logout_and_break(sleep_minutes)
        next_break_minutes[0] = next_cycle_minutes
        return True
    return False

def _click_lowest_tele_jewelry(base_name: str, max_charges: int, action: str = 'rub', retries: int = 5) -> bool:
    """
    Internal helper: clicks the lowest-charge version of a teleport jewelry item in inventory.
    Iterates from charge 1 → max_charges and clicks the first match found.
    """
    inv_data = inventory(item=base_name)
    if not inv_data or 'data' not in inv_data:
        print("No inventory data")
        return False

    items = inv_data['data']

    for charge in range(1, max_charges + 1):
        target_name = f"{base_name}({charge})"
        matching_item = next(
            (item for item in items if item.get('name', '').lower() == target_name.lower()),
            None
        )
        if matching_item:
            name = matching_item['name']
            print(f"Clicking lowest charge: {name}")

            for i in range(retries):
                if click_inventory(name, action=action, hover_only=False):
                    print(f"Clicked {name} successfully")
                    return True
                wait_for_next_tick()

            print(f"Failed to click {name} after {retries} attempts")
            return False

    print(f"No {base_name} found")
    return False


# Inventory helpers (unchanged)
def click_lowest_games_necklace(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("games necklace", 8, action, retries)


def click_lowest_glory(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("amulet of glory", 6, action, retries)


def click_lowest_ring_of_dueling(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("ring of dueling", 8, action, retries)


def click_lowest_combat_bracelet(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("combat bracelet", 6, action, retries)


def click_lowest_ring_of_wealth(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("ring of wealth", 5, action, retries)

# Inventory helpers (add this with the other click_lowest_ functions)
def click_lowest_necklace_of_passage(action: str = 'rub', retries: int = 5) -> bool:
    return _click_lowest_tele_jewelry("necklace of passage", 5, action, retries)



def click_equipped_necklace_of_passage(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Necklace of passage", action, retries)

def _click_equipped_jewelry(base_name: str, action: str = 'Rub', retries: int = 5) -> bool:
    """
    Internal helper for equipped jewelry: opens equipment tab first, then clicks with fuzzy matching.
    """
    # Open equipment tab (safe to click even if already open)
    if not click_widget('35913796', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=5, rand_y=5, clicks=1, sleep_interval=(0, 0)):
        print(f"Failed to open equipment tab for {base_name}")
        return False
    wait_for_next_tick()

    # Click the equipped item
    for i in range(retries):
        if click_widget_by_name(base_name, action=action, exact_match=False):
            print(f"Clicked equipped {base_name} ({action})")
            return True
        wait_for_next_tick()

    print(f"Failed to click equipped {base_name} ({action}) after {retries} attempts")
    return False


def click_equipped_glory(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Amulet of glory", action, retries)


def click_equipped_ring_of_dueling(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Ring of dueling", action, retries)


def click_equipped_games_necklace(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Games necklace", action, retries)


def click_equipped_combat_bracelet(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Combat bracelet", action, retries)


def click_equipped_ring_of_wealth(action: str = 'Rub', retries: int = 5) -> bool:
    return _click_equipped_jewelry("Ring of wealth", action, retries)