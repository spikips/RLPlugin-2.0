# nmz_bank.py - SMART VERSION (only withdraws what should be in normal bank)
from check_gear import check_gear
from modules.utils.banking import bank
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick
from potions import get_total_doses
import json
import os

def nmz_bank(withdraw_prayer_potions=True):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            style = config.get('style', 'range')
            withdraw_all_items = config.get('withdraw_all_items', {}).get(style, [])
            inventory_items = config.get('inventory_items', {}).get(style, [])
    except Exception:
        print("Failed to load config in nmz_bank.")
        return False

    gear_message, missing_items, inventory_items_coords = check_gear(prayer_fallback=withdraw_prayer_potions)
    print(gear_message)

    if missing_items:
        bank(deposit_inventory=True)

        print(f"Withdrawing missing gear items: {missing_items}")
        for item in missing_items:
            quantity = "all" if item in withdraw_all_items else "1"
            print(f"Withdrawing {item} (quantity={quantity})...")
            success = bank(withdraw=item, quantity=quantity)
            if not success:
                print(f"Failed to withdraw {item}")
                return False
            print(f"Successfully withdrew {item}")

        wait_for_tick(2)
        _, _, inventory_items_coords = check_gear()

        for item in missing_items:
            if item in inventory_items_coords:
                x, y = inventory_items_coords[item]
                success = select_menu_option(x, y, "Wield")
                if not success:
                    success = select_menu_option(x, y, "Wear")
                if not success:
                    success = select_menu_option(x, y, "Equip")
                if not success:
                    print(f"Failed to equip {item}")
                    return False
                print(f"Successfully equipped {item}")
            else:
                print(f"Item {item} not found in inventory after withdrawal")
                return False

    print("Withdrawing inventory items...")
    bank(deposit_inventory=True)
    wait_for_tick(1)

    for item_dict in inventory_items:
        item_name = item_dict.get('name')
        quantity = item_dict.get('quantity', '1')

        if "absorption" in item_name.lower() or "overload" in item_name.lower():
            continue

        if "prayer potion" in item_name.lower() and not withdraw_prayer_potions:
            print("FULL MODE active - skipping Prayer potion withdrawal")
            continue

        print(f"Withdrawing {item_name} (quantity={quantity})...")
        success = bank(withdraw=item_name, quantity=quantity)
        if not success:
            print(f"Failed to withdraw {item_name}")
            return False

    print("Banking complete.")
    return True


if __name__ == "__main__":
    print(nmz_bank())