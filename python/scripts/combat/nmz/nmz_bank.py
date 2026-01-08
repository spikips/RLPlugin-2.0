from check_gear import check_gear
from modules.utils.banking import bank
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick
import json
import os

def nmz_bank():
    """
    Withdraw all missing gear items if needed, wait for 2 ticks, then equip them using select_menu_option.
    Withdraws items with quantity based on withdraw_all_items ('all') or '1' otherwise.
    Tries 'Wield' first, then 'Wear' if 'Wield' is not available, then 'Equip' if 'Wear' is not available.
    Then, withdraw inventory items (e.g., dwarven rock cake, potions, runes).
    Returns True if all actions succeed, False otherwise.
    """
    # Load config.json for withdraw_all_items and inventory_items
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            style = config.get('style', 'range')
            withdraw_all_items = config.get('withdraw_all_items', {}).get(style, [])
            inventory_items = config.get('inventory_items', {}).get(style, [])
    except FileNotFoundError:
        print(f"{json_path} not found.")
        return False
    except json.JSONDecodeError:
        print("Invalid JSON in config.json.")
        return False

    # Get the gear check result
    gear_message, missing_items, inventory_items_coords = check_gear()
    print(gear_message)
    
    if missing_items:
        bank(deposit_inventory=True)

        # Withdraw all missing gear items
        print(f"Withdrawing missing gear items: {missing_items}")
        for item in missing_items:
            quantity = "all" if item in withdraw_all_items else "1"
            print(f"Withdrawing {item} (quantity={quantity})...")
            success = bank(withdraw=item, quantity=quantity)
            if not success:
                print(f"Failed to withdraw {item}")
                return False
            print(f"Successfully withdrew {item}")
        
        # Wait for 2 game ticks after all withdrawals
        print("Waiting for 2 game ticks after withdrawals...")
        wait_for_tick(2)
        
        # Refresh gear check to get updated inventory coordinates
        _, _, inventory_items_coords = check_gear()
        
        # Equip each gear item using select_menu_option, trying 'Wield' then 'Wear' then 'Equip'
        for item in missing_items:
            if item in inventory_items_coords:
                x, y = inventory_items_coords[item]
                # Try 'Wield' first
                print(f"Attempting to equip {item} at inventory coordinates ({x}, {y}) with action 'Wield'...")
                success = select_menu_option(x, y, "Wield")
                if not success:
                    # Fall back to 'Wear' if 'Wield' fails
                    print(f"'Wield' not available for {item}, trying 'Wear'...")
                    success = select_menu_option(x, y, "Wear")
                    if not success:
                        # Fall back to 'Equip' if 'Wear' fails
                        print(f"'Wear' not available for {item}, trying 'Equip'...")
                        success = select_menu_option(x, y, "Equip")
                        if not success:
                            print(f"Failed to equip {item} with 'Wield', 'Wear', and 'Equip'")
                            return False
                print(f"Successfully equipped {item}")
            else:
                print(f"Item {item} not found in inventory after withdrawal")
                return False
    
    # Withdraw inventory items (e.g., dwarven rock cake, overload and absorption potions, runes)
    print("Withdrawing inventory items...")
    # Deposit inventory first
    bank(deposit_inventory=True)
    wait_for_tick(1)
    # Withdraw inventory items from config
    for item_dict in inventory_items:
        item = item_dict.get('name')
        quantity = item_dict.get('quantity', '1')
        success = bank(withdraw=item, quantity=quantity)
        if not success:
            print(f"Failed to withdraw {item}")
            return False
    
    return True

if __name__ == "__main__":
    # For testing
    print(nmz_bank())