import sys
import random
import time
import re
from collections import Counter, defaultdict
from typing import Union

import keyboard

from modules.banking.bank_castlewars import open_inventory_tab
from modules.player_data.prayer.toggle_prayer import disable_all_prayer
from modules.widgets.widget import check_widget_text, click_widget, get_widget
from modules.core.plugin_client import gear, inventory, interact_options, bank_items
from modules.core.mouse_control import move, scroll
from modules.core.window_utils import runelite_window
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.camera import camera
from modules.object_data.game_object import click_gameobject
from modules.widgets.widget import click_widget_child
from modules.utils.banking import bank


# Comprehensive chargeable items (jewelry + common potions) - all lowercased
CHARGEABLE_ITEMS = {
    "amulet of glory",
    "combat bracelet",
    "ring of wealth",
    "games necklace",
    "ring of dueling",
    "skills necklace",
    "necklace of passage",
    "digsite pendant",
    "burning amulet",
    "pharaoh's sceptre",
    "slayer ring",
    "binding necklace",
    "bracelet of ethereum",
    "bracelet of slaughter",
    "castle wars bracelet",
    "celestial ring",
    "desert amulet",
    "dodgy necklace",
    "explorer's ring",
    "flamtaer bracelet",
    "ring of endurance",
    "ring of pursuit",
    "ring of recoil",
    "ring of returning",
    "prayer potion",
    "divine super combat potion",
    "super combat potion",
    "super restore",
    "saradomin brew",
    "zamorak brew",
    "antidote++",
    "anti-venom+",
    "stamina potion",
    "extended antifire",
    "extended super antifire",
    "waterskin"
}

# Potions where we require the full 4-dose version specifically (no (1)/(2)/(3) accepted as "good")
FULL_DOSE_POTIONS = {
    "prayer potion",
    "divine super combat potion",
    "super combat potion",
    "super restore",
}

# Widget IDs for accurate inventory reading
BANK_INVENTORY_WIDGET_ID = "983043"
SIDEBAR_INVENTORY_WIDGET_ID = "9764864"
INVENTORY_TAB_WIDGET_ID = "35913795"
INVENTORY_TAB_OPEN_SPRITE = 1030


def close_bank():
    keyboard.press('esc')
    time.sleep(random.uniform(0.05, 0.1))
    keyboard.release('esc')
    wait_for_next_tick()


def get_charge(name: str) -> int:
    match = re.search(r'\((\d+)\)$', name or '')
    return int(match.group(1)) if match else 0


def clean_item_name(name: str) -> str:
    if not name:
        return ''
    return re.sub(r'\s*\(\d+\)$', '', name).strip().lower()


def get_inventory_data() -> list[dict]:
    widget_id_to_use = None

    if is_bank_open():
        widget_id_to_use = BANK_INVENTORY_WIDGET_ID
    else:
        if open_inventory_tab():
            widget_id_to_use = SIDEBAR_INVENTORY_WIDGET_ID

    items = []
    if widget_id_to_use:
        try:
            widget = get_widget(widget_id_to_use)
            if widget and 'children' in widget:
                children = widget.get('children', [])
                for child in children:
                    raw_name = child.get('name', '')
                    if not raw_name:
                        continue
                    name = re.sub(r'<col=[0-9a-fA-F]+>|</col>', '', raw_name).strip()
                    if not name:
                        continue
                    qty = child.get('quantity', 1)
                    mp = child.get('random_clickpoint')
                    item_dict = {
                        'name': name,
                        'quantity': qty,
                    }
                    if mp:
                        item_dict['middle_point'] = {'x': mp['x'], 'y': mp['y']}
                    items.append(item_dict)

                if items:
                    return items
        except Exception:
            pass

    return inventory().get('data', [])


def has_suitable_in_inventory(base_name: str) -> bool:
    base_name = clean_item_name(base_name)
    inv_data = inventory().get('data', [])
    for item in inv_data:
        clean = clean_item_name(item.get('name', ''))
        if clean == base_name:
            charge = get_charge(item.get('name', ''))
            if base_name in CHARGEABLE_ITEMS:
                if charge > 0:
                    return True
            else:
                return True
    return False


def cleanup_inventory(target_gear: list[str] | None, target_inventory: dict[str, Union[int, str]] | None) -> bool:
    success = True

    normalized_target_gear = [clean_item_name(g) for g in (target_gear or [])]
    normalized_target_inventory = {clean_item_name(k): v for k, v in (target_inventory or {}).items()}

    target_gear_bases = set(normalized_target_gear)
    target_inv_bases = set(normalized_target_inventory.keys())
    target_bases = target_gear_bases.union(target_inv_bases)
    current_gear_set = get_current_gear_set()

    if not target_bases:
        bank(deposit_inventory=True)
        wait_for_tick(2)
        return True

    current_before = get_current_inventory_dict()

    inv_data = get_inventory_data()
    if not inv_data:
        return True

    exact_totals = Counter()
    deposit_counter = Counter()
    base_instances = defaultdict(list)

    for item in inv_data:
        name = item.get('name', '')
        if not name:
            continue
        base = clean_item_name(name)
        charge = get_charge(name)
        qty = item.get('quantity', 1)
        base_instances[base].append({'name': name, 'charge': charge, 'qty': qty})
        exact_totals[name] += qty

    for base, insts in base_instances.items():
        inv_desired_raw = normalized_target_inventory.get(base, 0)

        if inv_desired_raw == "all":
            continue

        inv_keep = inv_desired_raw
        gear_keep = 1 if base in target_gear_bases and (base not in current_gear_set or (base in CHARGEABLE_ITEMS and get_equipped_charge(base) == 0)) else 0
        desired_keep = max(inv_keep, gear_keep)
        total_qty = sum(i['qty'] for i in insts)

        if desired_keep == 0 and base not in target_bases:
            for inst in insts:
                deposit_counter[inst['name']] += inst['qty']
            continue

        if base in CHARGEABLE_ITEMS:
            uncharged_insts = [i for i in insts if i['charge'] == 0]
            if base in FULL_DOSE_POTIONS:
                # For full-dose potions, treat anything other than (4) as unwanted (deposit lowers)
                low_dose_insts = [i for i in insts if 0 < i['charge'] < 4]
                charged_insts = [i for i in insts if i['charge'] == 4]
                for u in uncharged_insts + low_dose_insts:
                    deposit_counter[u['name']] += u['qty']
            else:
                charged_insts = [i for i in insts if i['charge'] > 0]
                for u in uncharged_insts:
                    deposit_counter[u['name']] += u['qty']

            charged_insts.sort(key=lambda i: i['charge'], reverse=True)
            keep_needed = desired_keep
            current_kept = 0

            for c in charged_insts:
                if current_kept >= keep_needed:
                    deposit_counter[c['name']] += c['qty']
                    continue

                keep_this = min(c['qty'], keep_needed - current_kept)
                if keep_this < c['qty']:
                    excess_this = c['qty'] - keep_this
                    deposit_counter[c['name']] += excess_this
                current_kept += keep_this

        else:
            excess = max(0, total_qty - desired_keep)
            if excess == 0:
                continue

            remaining_excess = excess
            for inst in insts:
                if remaining_excess <= 0:
                    break
                dep_this = min(remaining_excess, inst['qty'])
                deposit_counter[inst['name']] += dep_this
                remaining_excess -= dep_this

    if deposit_counter:
        for exact_name, dep_qty in deposit_counter.items():
            total_available = exact_totals.get(exact_name, 0)
            if dep_qty == total_available and total_available > 0:
                bank(deposit=exact_name, quantity="all")
            else:
                if dep_qty in [1, 5, 10]:
                    bank(deposit=exact_name, quantity=str(dep_qty))
                else:
                    bank(deposit=exact_name, quantity="x", amount=dep_qty)
        wait_for_tick(1)

    return success


def get_equipped_charge(base_name: str) -> int:
    base_name = clean_item_name(base_name)
    gear_raw = gear().get('data', {})
    for item_name in gear_raw.keys():
        if clean_item_name(item_name) == base_name:
            return get_charge(item_name)
    return 0


def get_current_gear_set() -> set[str]:
    gear_raw = gear().get('data', {})
    return {clean_item_name(name) for name in gear_raw.keys() if name}


def equip_gear_item(base_name: str, max_retries: int = 3) -> bool:
    base_name = clean_item_name(base_name)
    for retry in range(1, max_retries + 1):
        inv_data = inventory().get('data', [])
        matching_items = [
            item for item in inv_data
            if clean_item_name(item.get('name', '')) == base_name and item.get('middle_point')
        ]

        if not matching_items:
            return False

        item = random.choice(matching_items)
        mp = item['middle_point']
        rl_x, rl_y = runelite_window(0, 0)

        move(mp['x'] + rl_x, mp['y'] + rl_y, button='right')
        time.sleep(random.uniform(0.05, 0.12))

        options = interact_options()
        if not options or 'data' not in options:
            wait_for_tick(1)
            continue

        equip_options = ["Wield", "Wear", "Equip"]
        target_opt = next((opt for opt in options['data'] if opt.get('option', '') in equip_options), None)
        if not target_opt:
            wait_for_tick(1)
            continue

        opt_mp = target_opt.get('middle_point', {})
        if not opt_mp:
            wait_for_tick(1)
            continue

        move(opt_mp['x'] + rl_x, opt_mp['y'] + rl_y, button='left')
        wait_for_tick(1)

        equipped_charge = get_equipped_charge(base_name)
        if equipped_charge > 0 or base_name not in CHARGEABLE_ITEMS:
            return True

    return False


def withdraw_highest(base_name: str, quantity: int = 1) -> bool:
    if quantity <= 0:
        return True

    base_name = clean_item_name(base_name)
    bank_data = bank_items().get('data', [])
    if not bank_data:
        return False

    is_chargeable = base_name in CHARGEABLE_ITEMS

    candidates = [
        item for item in bank_data
        if clean_item_name(item.get('name', '')) == base_name
        and item.get('quantity', 0) > 0
    ]

    if is_chargeable:
        candidates = [item for item in candidates if get_charge(item.get('name', '')) > 0]

    if not candidates:
        return False

    if is_chargeable:
        candidates.sort(key=lambda i: get_charge(i.get('name', '')), reverse=True)

    remaining = quantity
    withdrawn = 0

    for item in candidates:
        if remaining <= 0:
            break

        exact_name = item['name']
        available = item.get('quantity', 0)
        take = min(remaining, available)

        if take == available and available > 0:
            quan = "all"
            am = None
        elif take in [1, 5, 10]:
            quan = str(take)
            am = None
        else:
            quan = "x"
            am = take

        success = bank(withdraw=exact_name, quantity=quan, amount=am)
        if success:
            withdrawn += take
            remaining -= take

    return withdrawn == quantity


def get_current_inventory_dict() -> dict[str, int]:
    inv_raw = get_inventory_data()
    counter = Counter()
    for item in inv_raw:
        clean = clean_item_name(item.get('name', ''))
        if clean:
            qty = item.get('quantity', 1)
            counter[clean] += qty
    return dict(counter)


def setup_gear(target_gear: list[str] | None) -> bool:
    if not target_gear:
        return True

    normalized_target_gear = [clean_item_name(g) for g in target_gear]

    success = True
    max_loops = 6

    for loop_num in range(1, max_loops + 1):
        current_gear_set = get_current_gear_set()
        to_update = []

        for base_name in normalized_target_gear:
            charge = get_equipped_charge(base_name)
            if base_name not in current_gear_set or (base_name in CHARGEABLE_ITEMS and charge == 0):
                to_update.append(base_name)

        if not to_update:
            return True

        for name in to_update:
            if has_suitable_in_inventory(name):
                continue

            if name in CHARGEABLE_ITEMS:
                withdraw_highest(name)
            else:
                bank(withdraw=name, quantity="1")

        for name in to_update:
            if not has_suitable_in_inventory(name):
                success = False
                continue

            wait_for_tick(1)
            if not equip_gear_item(name, max_retries=2):
                success = False

    return success


def setup_inventory(target_inventory: dict[str, Union[int, str]] | None) -> bool:
    if not target_inventory:
        return True

    normalized_target_inventory = {clean_item_name(k): v for k, v in target_inventory.items()}

    success = True

    # Handle "all" withdrawals
    all_items = [name for name, qty in normalized_target_inventory.items() if qty == "all"]
    for name in all_items:
        if name in CHARGEABLE_ITEMS:
            success = False
            continue
        bank(withdraw=name, quantity="all")

    # Exact quantities
    exact_items = {name: qty for name, qty in normalized_target_inventory.items() if isinstance(qty, int)}

    if exact_items:
        max_loops = 8
        for loop_num in range(1, max_loops + 1):
            current = get_current_inventory_dict()
            missing = {}

            for name, target in exact_items.items():
                curr_qty = current.get(name, 0)
                need = target - curr_qty
                if need > 0:
                    missing[name] = need

            if not missing:
                break

            for name, need in missing.items():
                if name in CHARGEABLE_ITEMS:
                    withdraw_highest(name, quantity=need)
                else:
                    if need in [1, 5, 10]:
                        quan = str(need)
                        am = None
                    else:
                        quan = "x"
                        am = need
                    bank(withdraw=name, quantity=quan, amount=am)

            wait_for_next_tick(1)

    return success


def is_bank_open() -> bool:
    data = bank_items().get('data', [])
    return len(data) > 0


def is_gear_perfect(target_gear: list[str] | None) -> bool:
    if not target_gear:
        return True

    normalized_target_gear = [clean_item_name(g) for g in target_gear]
    current_set = get_current_gear_set()

    for base in normalized_target_gear:
        if base not in current_set:
            return False
        if base in CHARGEABLE_ITEMS:
            if get_equipped_charge(base) <= 0:
                return False
    return True


def is_inventory_perfect(target_inventory: dict[str, Union[int, str]] | None) -> bool:
    if not target_inventory:
        return True

    normalized_target_inventory = {clean_item_name(k): v for k, v in target_inventory.items()}
    inv_data = get_inventory_data()
    total_current = Counter()
    good_current = Counter()
    all_bases = set()

    for item in inv_data:
        name = item.get('name', '')
        if not name:
            continue
        base = clean_item_name(name)
        all_bases.add(base)
        qty = item.get('quantity', 1)
        total_current[base] += qty
        charge = get_charge(name)
        if base in FULL_DOSE_POTIONS:
            if charge == 4:
                good_current[base] += qty
        elif charge > 0 or base not in CHARGEABLE_ITEMS:
            good_current[base] += qty

    target_bases = set(normalized_target_inventory.keys())
    extra_bases = all_bases - target_bases
    if extra_bases:
        return False

    for base, desired_raw in normalized_target_inventory.items():
        total_qty = total_current[base]
        good_qty = good_current[base]

        if isinstance(desired_raw, int):
            if good_qty < desired_raw:
                return False
            if total_qty > desired_raw:
                return False
        elif desired_raw == "all":
            if good_qty == 0:
                return False

    return True


def open_bank_generic(bank_object_id: str, bank_action: str = "Bank", radius: int = 20):
    """Opens a bank by clicking a game object ID. No teleporting or walking.
    Ensures no overlay UI is present before clicking the world object (prevents
    right-click landing on inventory/bank panel items instead of the banker).
    """
    close_bank()
    for i in range(5):
        if click_gameobject(bank_object_id, bank_action, radius=radius):
            # Poll for the bank interface to actually be open (bank_items non-empty)
            for _ in range(8):
                if is_bank_open():
                    wait_till_character_stopped_moving(required_idle_ticks=2)
                    wait_for_next_tick(1)
                    return True
                wait_for_next_tick()
            # Bank did not register open after this click; retry the object click
        wait_for_next_tick()
    print(f"Failed to open bank using object {bank_object_id} with action '{bank_action}'")
    return False


def banking_function(
    target_gear: list[str] | None = None,
    target_inventory: dict[str, Union[int, str]] | None = None,
    bank_object_id: str = "4483",
    bank_action: str = "Use",
    bank_radius: int = 20
):
    """
    Generic banking function.
    - bank_object_id: The game object ID of the bank (e.g. "55199" for buffalo bank)
    - bank_action: The action to use when clicking the object (usually "Bank" or "Use")
    """

    # Early skip if already perfect
    gear_ok = is_gear_perfect(target_gear)
    inv_ok = is_inventory_perfect(target_inventory)

    if gear_ok and inv_ok:
        print("Player is already perfectly geared and inventoried – skipping banking.")
        return True

    # Open the bank using the provided object ID (no teleport)
    if not is_bank_open():
        if not open_bank_generic(bank_object_id, bank_action, bank_radius):
            print("Failed to open bank.")
            return False

    # Perform banking
    if cleanup_inventory(target_gear, target_inventory):
        close_bank()
        open_bank_generic(bank_object_id, bank_action, bank_radius)

    if target_gear:
        print("Setting up gear...")
        setup_gear(target_gear)
        cleanup_inventory(target_gear, target_inventory)

    if target_inventory:
        print("Setting up inventory...")
        setup_inventory(target_inventory)

    print("Banking complete.")
    keyboard.press('esc')
    time.sleep(random.uniform(0.03, 0.08))
    keyboard.release('esc')
    wait_for_next_tick(1)

    return True


# Example usage:
# target_gear = ["Blood moon helm", "Blood moon chestplate", ...]
# target_inventory = {"Divine super combat potion(4)": 4, "Prayer potion(4)": 4, "Potato with cheese": 26}
#
# banking_function(
#     target_gear=target_gear,
#     target_inventory=target_inventory,
#     bank_object_id="55199",
#     bank_action="Bank"
# )
