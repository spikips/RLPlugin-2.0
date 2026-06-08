import sys
import random
import time
import re
from collections import Counter, defaultdict
from typing import Union

import keyboard

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
from modules.utils.automatic_scripting.small_functions import (
    click_lowest_ring_of_dueling,
    click_equipped_ring_of_dueling
)
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

# Add these constants near the top (with the other widget IDs)
BANK_INVENTORY_WIDGET_ID = "983043"      # Inventory widget when bank is open
SIDEBAR_INVENTORY_WIDGET_ID = "9764864"  # Inventory widget when bank is closed (sidebar open)

INVENTORY_TAB_WIDGET_ID = "35913795"     # The widget that shows the inventory tab icon/state
INVENTORY_TAB_OPEN_SPRITE = 1030         # Sprite when inventory tab is active

def close_bank():
    keyboard.press('esc')
    time.sleep(random.uniform(0.05, 0.1))
    keyboard.release('esc')
    wait_for_next_tick()

def reopen_bank():
    for _ in range(2):
        if click_gameobject("4483", 'Use', tile=(2444, 3083), radius=20):
            wait_till_character_stopped_moving(required_idle_ticks=1)
            return True
        wait_for_tick(1)
    print("Failed to reopen bank")
    return False


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
        print("Bank is open – using bank inventory widget")
    else:
        print("Bank is closed – ensuring inventory tab open for sidebar widget")
        if open_inventory_tab():
            widget_id_to_use = SIDEBAR_INVENTORY_WIDGET_ID
        else:
            print("Could not open inventory tab – will fallback to plugin inventory()")

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
                    print(f"Successfully parsed inventory via widget {widget_id_to_use} (accurate quantities)")
                    return items
        except Exception as e:
            print(f"Widget inventory parsing failed for {widget_id_to_use} ({e})")

    print("All widget attempts failed – falling back to plugin inventory() (may misread large stacks)")
    return inventory().get('data', [])



def has_suitable_in_inventory(base_name: str) -> bool:
    base_name = clean_item_name(base_name)  # ensure normalized
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

    # Normalize targets for case-insensitive matching
    normalized_target_gear = [clean_item_name(g) for g in (target_gear or [])]
    normalized_target_inventory = {clean_item_name(k): v for k, v in (target_inventory or {}).items()}

    target_gear_bases = set(normalized_target_gear)
    target_inv_bases = set(normalized_target_inventory.keys())
    target_bases = target_gear_bases.union(target_inv_bases)
    current_gear_set = get_current_gear_set()

    if not target_bases:
        print("No targets defined -> falling back to deposit entire inventory")
        bank(deposit_inventory=True)
        wait_for_tick(2)
        return True

    print("Starting selective inventory cleanup")
    current_before = get_current_inventory_dict()
    print(f"Inventory before cleanup (base counts): { {k: v for k, v in current_before.items() if v > 0} }")

    inv_data = get_inventory_data()
    if not inv_data:
        print("Inventory empty -> nothing to clean")
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
            print(f"Processing {base}: desired keep = all, current total = {sum(i['qty'] for i in insts)}")
            print(f"  -> Keeping everything (desired 'all')")
            continue

        inv_keep = inv_desired_raw
        gear_keep = 1 if base in target_gear_bases and (base not in current_gear_set or (base in CHARGEABLE_ITEMS and get_equipped_charge(base) == 0)) else 0

        desired_keep = max(inv_keep, gear_keep)

        total_qty = sum(i['qty'] for i in insts)
        print(f"Processing {base}: desired keep = {desired_keep} (inv: {inv_keep}, gear min: {gear_keep}), current total = {total_qty}")

        if desired_keep == 0 and base not in target_bases:
            for inst in insts:
                deposit_counter[inst['name']] += inst['qty']
            continue

        if base in CHARGEABLE_ITEMS:
            uncharged_insts = [i for i in insts if i['charge'] == 0]
            charged_insts = [i for i in insts if i['charge'] > 0]

            for u in uncharged_insts:
                deposit_counter[u['name']] += u['qty']
                print(f"  -> Depositing {u['qty']} {u['name']} (uncharged)")

            charged_insts.sort(key=lambda i: i['charge'], reverse=True)
            keep_needed = desired_keep
            current_kept = 0
            print(f"  -> Prioritising highest charges, need to keep {keep_needed} total")

            for c in charged_insts:
                if current_kept >= keep_needed:
                    deposit_counter[c['name']] += c['qty']
                    print(f"  -> Depositing {c['qty']} {c['name']} (excess/low priority)")
                    continue

                keep_this = min(c['qty'], keep_needed - current_kept)
                if keep_this < c['qty']:
                    excess_this = c['qty'] - keep_this
                    deposit_counter[c['name']] += excess_this
                    print(f"  -> Depositing {excess_this} {c['name']} (partial excess)")
                else:
                    print(f"  -> Keeping all {c['qty']} {c['name']} (high priority)")

                current_kept += keep_this

        else:
            excess = max(0, total_qty - desired_keep)
            if excess == 0:
                print(f"  -> Quantity correct -> nothing to deposit")
                continue

            print(f"  -> Depositing excess {excess} (non-chargeable)")

            remaining_excess = excess
            for inst in insts:
                if remaining_excess <= 0:
                    break
                dep_this = min(remaining_excess, inst['qty'])
                deposit_counter[inst['name']] += dep_this
                remaining_excess -= dep_this

    if deposit_counter:
        print(f"Performing {len(deposit_counter)} grouped deposit operations")
        for exact_name, dep_qty in deposit_counter.items():
            total_available = exact_totals.get(exact_name, 0)

            if dep_qty == total_available and total_available > 0:
                print(f"  Depositing all {exact_name} (fast Deposit-All)")
                bank(deposit=exact_name, quantity="all")
            else:
                if dep_qty in [1, 5, 10]:
                    print(f"  Depositing {dep_qty} {exact_name} (preset button)")
                    bank(deposit=exact_name, quantity=str(dep_qty))
                else:
                    print(f"  Depositing {dep_qty} {exact_name} (Deposit-X)")
                    bank(deposit=exact_name, quantity="x", amount=dep_qty)

        wait_for_tick(1)
    else:
        print("No items to deposit")
        return False

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
            print(f"{base_name} not found in inventory (retry {retry}/{max_retries})")
            return False

        item = random.choice(matching_items)
        mp = item['middle_point']
        rl_x, rl_y = runelite_window(0, 0)

        move(mp['x'] + rl_x, mp['y'] + rl_y, button='right')
        time.sleep(random.uniform(0.05, 0.12))

        options = interact_options()
        if not options or 'data' not in options:
            print("Failed to get interact options")
            wait_for_tick(1)
            continue

        equip_options = ["Wield", "Wear", "Equip"]
        target_opt = next((opt for opt in options['data'] if opt.get('option', '') in equip_options), None)
        if not target_opt:
            print(f"No equip option found for {base_name}")
            wait_for_tick(1)
            continue

        opt_mp = target_opt.get('middle_point', {})
        if not opt_mp:
            wait_for_tick(1)
            continue

        move(opt_mp['x'] + rl_x, opt_mp['y'] + rl_y, button='left')
        print(f"Attempted to equip {base_name} (retry {retry}/{max_retries})")
        wait_for_tick(1)

        equipped_charge = get_equipped_charge(base_name)
        if equipped_charge > 0 or base_name not in CHARGEABLE_ITEMS:
            print(f"Successfully equipped {base_name} (charges: {equipped_charge})")
            return True

        print(f"{base_name} equipped but 0 charges after attempt {retry}")

    print(f"Failed to equip charged {base_name} after {max_retries} retries")
    return False


def withdraw_highest(base_name: str, quantity: int = 1) -> bool:
    if quantity <= 0:
        return True

    base_name = clean_item_name(base_name)
    bank_data = bank_items().get('data', [])
    if not bank_data:
        print("Failed to get bank data")
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
        print(f"No{' charged' if is_chargeable else ''} {base_name} found in bank")
        return False

    if is_chargeable:
        candidates.sort(key=lambda i: get_charge(i.get('name', '')), reverse=True)

    remaining = quantity
    withdrawn = 0

    print(f"Withdrawing up to {quantity} × {base_name} (highest charge/dose first)")

    for item in candidates:
        if remaining <= 0:
            break

        exact_name = item['name']
        available = item.get('quantity', 0)
        take = min(remaining, available)

        if take == available and available > 0:
            quan = "all"
            am = None
            print(f"  Withdrawing all {exact_name} ({available})")
        elif take in [1, 5, 10]:
            quan = str(take)
            am = None
            print(f"  Withdrawing {take} {exact_name} (preset button)")
        else:
            quan = "x"
            am = take
            print(f"  Withdrawing {take} {exact_name} (Withdraw-X)")

        success = bank(withdraw=exact_name, quantity=quan, amount=am)
        if not success:
            print(f"  Failed to withdraw {take} {exact_name}")
            continue

        withdrawn += take
        remaining -= take

    if withdrawn == quantity:
        print(f"Successfully withdrew {quantity} × {base_name}")
        wait_for_tick(1)
        return True
    else:
        print(f"Only withdrew {withdrawn}/{quantity} × {base_name} (ran out of charged stock)")
        return False


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

    # Normalize gear list
    normalized_target_gear = [clean_item_name(g) for g in target_gear]

    success = True
    max_loops = 6

    for loop_num in range(1, max_loops + 1):
        equipped_charges = {base: get_equipped_charge(base) for base in normalized_target_gear}
        print(f"Gear loop {loop_num}/{max_loops} – current equipped charges: {equipped_charges}")

        current_gear_set = get_current_gear_set()
        to_update = []
        for base_name in normalized_target_gear:
            charge = get_equipped_charge(base_name)
            if base_name not in current_gear_set or (base_name in CHARGEABLE_ITEMS and charge == 0):
                to_update.append(base_name)

        if not to_update:
            print("Gear fully equipped and charged")
            return True

        print(f"  Need to update: {to_update}")

        for name in to_update:
            if has_suitable_in_inventory(name):
                print(f"  Suitable {name} already in inventory – skipping withdraw")
                continue

            print(f"  Withdrawing suitable {'highest-charge ' if name in CHARGEABLE_ITEMS else ''}{name}")
            if name in CHARGEABLE_ITEMS:
                if not withdraw_highest(name):
                    print(f"  Failed to withdraw charged {name}")
                    success = False
            else:
                if not bank(withdraw=name, quantity="1"):
                    print(f"  Failed to withdraw {name}")
                    success = False

        for name in to_update:
            if not has_suitable_in_inventory(name):
                print(f"  No suitable {name} in inventory – cannot equip")
                success = False
                continue

            wait_for_tick(1)
            if not equip_gear_item(name, max_retries=2):
                print(f"  Failed to equip {name}")
                success = False

    print("Gear setup failed after max loops")
    return success


def setup_inventory(target_inventory: dict[str, Union[int, str]] | None) -> bool:
    if not target_inventory:
        return True

    # Normalize inventory dict
    normalized_target_inventory = {clean_item_name(k): v for k, v in target_inventory.items()}

    success = True

    # Step 1: Handle "all" withdrawals first
    all_items = [name for name, qty in normalized_target_inventory.items() if qty == "all"]
    for name in all_items:
        if name in CHARGEABLE_ITEMS:
            print(f"Cannot withdraw 'all' for chargeable item {name} – skipping")
            success = False
            continue

        print(f"Withdrawing all {name}")
        if not bank(withdraw=name, quantity="all"):
            print(f"Failed to withdraw all {name}")
            success = False

    # Step 2: Exact quantities
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
                print("All exact-quantity items are now in inventory")
                break

            print(f"Withdrawal loop {loop_num}/{max_loops}: missing {missing}")

            for name, need in missing.items():
                if name in CHARGEABLE_ITEMS:
                    print(f"Withdrawing {need} × highest-charge {name}")
                    if not withdraw_highest(name, quantity=need):
                        print(f"Failed to withdraw the full {need} × {name}")
                        success = False
                else:
                    print(f"Withdrawing {need} × {name}")
                    if need in [1, 5, 10]:
                        quan = str(need)
                        am = None
                    else:
                        quan = "x"
                        am = need

                    if not bank(withdraw=name, quantity=quan, amount=am):
                        print(f"Failed to withdraw {need} {name}")
                        success = False
            
            wait_for_next_tick(1)

        else:
            print("Max withdrawal loops reached – some exact items may still be missing")
            success = False

    print("Inventory setup complete")
    return success


def is_wearing_ring_of_dueling() -> bool:
    gear_data = gear().get('data', {})
    for item_name in gear_data.keys():
        if clean_item_name(item_name) == "ring of dueling":
            return True
    return False

def teleport_and_open_bank():
    print("Starting Castle Wars bank teleport...")
    at_castle_wars = False

    if is_wearing_ring_of_dueling():
        print("Ring of Dueling equipped – teleporting directly")
        for i in range(5):
            if click_equipped_ring_of_dueling(action='Castle Wars'):
                wait_for_tile_change(timeout_ticks=6, max_retries=1)
                wait_for_next_tick()
                at_castle_wars = True
                break
            wait_for_next_tick()
            # if i == 4:
            #     sys.exit("Failed to click equipped Ring of Dueling (Castle Wars)")
    else:
        print("Ring of Dueling not equipped – rubbing lowest charge")
        while not at_castle_wars:
            if click_lowest_ring_of_dueling(action='Rub'):
                print("Selecting Castle Wars from dialogue")
                for i in range(3):
                    if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=2, right_click=False, action=None):
                        if wait_for_tile_change(timeout_ticks=6, max_retries=1):
                            wait_for_next_tick(2)
                            at_castle_wars = True
                            break
                        wait_for_next_tick()

                    wait_for_next_tick()
                break
            wait_for_next_tick()
            # if i == 4:
            #     sys.exit("Failed to click lowest Ring of Dueling (Rub)")



    if not at_castle_wars:
        for i in range(7):
            click_widget('35913776', rand_x=10, rand_y=10)
            time.sleep(0.3)
            click_widget('46333957', rand_x=10, rand_y=10)
            time.sleep(0.3)
            click_widget('35913776')
            time.sleep(0.3)
            click_widget('4980746', rand_x=50, rand_y=5)
            time.sleep(0.3)

            # 4980758       
            for child in range(8):
                castle_wars = check_widget_text('4980758', child_index=child)
                if castle_wars and 'castle wars' in castle_wars.lower():
                    print('clicking castle wars widget')
                    click_widget_child('4980758', child_index=child)
                    break

            time.sleep(0.3)
            click_widget('4980768', rand_x=5, rand_y=5)

            if wait_for_tile_change(timeout_ticks=40):
                print("Successfully teleported to Castle Wars using widgets.")
                break
            print(f'unable to teleport to castle wars, sleeping for 3-4min and retrying {i}')
            time.sleep(random.randint(3,4)*60)


    print("Teleported – setting camera and opening bank")
    for i in range(3):
        if camera(pitch=434, yaw=1710, zoom=300, speed=10):
            break
        if i == 2:
            sys.exit("Failed to set camera")

    for i in range(2):
        if click_gameobject("4483", 'Use', tile=(2444, 3083), radius=20):
            wait_till_character_stopped_moving(required_idle_ticks=2)
            wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            sys.exit("Failed to open bank chest")

    print("Bank opened")


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
            print(f"Missing equipped: {base}")
            return False
        if base in CHARGEABLE_ITEMS:
            charge = get_equipped_charge(base)
            if charge <= 0:
                print(f"Equipped {base} is uncharged")
                return False
    print("Gear is already perfect")
    return True

def is_inventory_tab_open() -> bool:
    widget = get_widget(INVENTORY_TAB_WIDGET_ID)
    if widget:
        return widget.get('spriteId', -1) == INVENTORY_TAB_OPEN_SPRITE
    return False

def open_inventory_tab(max_attempts: int = 3) -> bool:
    for attempt in range(1, max_attempts + 1):
        if is_inventory_tab_open():
            print("Inventory tab already open")
            return True
        print(f"Inventory tab not open (attempt {attempt}/{max_attempts}), pressing F1")
        keyboard.press_and_release('f1')
        time.sleep(random.uniform(0.15, 0.35))
        wait_for_tick(2)
    print("Failed to open inventory tab after max attempts")
    return False

def is_inventory_perfect(target_inventory: dict[str, Union[int, str]] | None) -> bool:
    if not target_inventory:
        return True

    # Normalize inventory dict
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
        if charge > 0 or base not in CHARGEABLE_ITEMS:
            good_current[base] += qty

    target_bases = set(normalized_target_inventory.keys())
    extra_bases = all_bases - target_bases
    if extra_bases:
        print(f"Useless/extra item types in inventory: {extra_bases}")
        return False

    for base, desired_raw in normalized_target_inventory.items():
        total_qty = total_current[base]
        good_qty = good_current[base]

        if isinstance(desired_raw, int):
            if good_qty < desired_raw:
                print(f"Insufficient charged/good {base}: {good_qty} < {desired_raw}")
                return False
            if total_qty > desired_raw:
                print(f"Excess items for {base}: {total_qty} > {desired_raw} (likely uncharged/low-dose extras)")
                return False
        elif desired_raw == "all":
            if good_qty == 0:
                print(f"No {base} in inventory")
                return False
            if base == "steel cannonball" and good_qty < 20000:  # Adjust threshold as needed
                print(f"Low on {base}: {good_qty} (recommend topping up)")
                return False

    print("Inventory is already perfect (quantities + no extras/uncharged junk)")
    return True

def bank_castlewars(target_gear: list[str] | None = None, target_inventory: dict[str, Union[int, str]] | None = None):
    # === EARLY SKIP IF ALREADY PERFECT ===
    gear_ok = is_gear_perfect(target_gear)
    inv_ok = is_inventory_perfect(target_inventory)
    if gear_ok and inv_ok:
        print("Player is already perfectly geared and inventoried – skipping Castle Wars banking entirely")
        return

    # === SMART BANK OPENING (only if needed) ===
    if is_bank_open():
        print("Bank interface already open – proceeding")
    else:
        camera(pitch=434, yaw=1710, zoom=300, speed=10)
        disable_all_prayer()
        print("Bank not open – attempting to open locally first...")
        opened_locally = False
        for _ in range(2):
            if click_gameobject("4483", 'Use', tile=(2444, 3083), radius=30):
                wait_till_character_stopped_moving(required_idle_ticks=2)
                wait_for_tick(2)
                if is_bank_open():
                    print("Successfully opened bank locally (no teleport needed)")
                    opened_locally = True
                    break
            wait_for_tick(1)

        if not opened_locally:
            print("Local open failed – falling back to Ring of Dueling teleport")
            teleport_and_open_bank()

    # === REST OF BANKING LOGIC (only runs if not already perfect) ===
    if cleanup_inventory(target_gear, target_inventory):
        close_bank()
        reopen_bank()

    if target_gear:
        print("Setting up gear (replacing missing/uncharged equipped items)...")
        setup_gear(target_gear)

        print("Post-gear cleanup (removing displaced uncharged items)...")
        cleanup_inventory(target_gear, target_inventory)

    if target_inventory:
        print("Setting up inventory (withdrawing missing items)...")
        setup_inventory(target_inventory)

    print("Castle Wars banking complete -> precise charged gear + exact inventory quantities")
    keyboard.press('esc')
    time.sleep(random.uniform(0.039, 0.081))
    keyboard.release('esc')
    wait_for_next_tick(1)

    
# print(get_inventory_data())

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
#     "Prayer potion": 6,
#     "Games necklace": 1,
#     "Amulet of glory": 1,
#     "Ring of dueling": 2,
#     "Cannon barrels": 1,
#     "Cannon furnace": 1,
#     "Cannon base": 1,
#     "Cannon stand": 1,
#     "Steel cannonball": "all",
#     "Coins": 1000,
#     "Waterskin": 6
# }

# bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
