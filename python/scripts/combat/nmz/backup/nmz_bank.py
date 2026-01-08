from check_gear import check_gear
from modules.utils.banking import bank
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick
from gear_config import AMMO_ITEMS
import time
import random

def nmz_bank():
    """
    Withdraw all missing gear items, wait for 2 ticks, then equip them using select_menu_option.
    Withdraws ammo items with quantity='all', others with quantity='1'.
    Tries 'Wield' first, then 'Wear' if 'Wield' is not available.
    Returns True if all actions succeed, False otherwise.
    """
    # Get the gear check result
    gear_message, missing_items, inventory_items = check_gear()
    print(gear_message)
    
    # If all gear is equipped, no need to withdraw or equip
    if not missing_items:
        prayer_pot = bank(withdraw="prayer potion(4)", quantity="all", deposit_inventory=True)
        print("prayer pot", prayer_pot)
        return True
    
    bank(deposit_inventory=True)

    # Withdraw all missing gear items
    print(f"Withdrawing missing gear items: {missing_items}")
    for item in missing_items:
        quantity = "all" if item in AMMO_ITEMS else "1"
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
    _, _, inventory_items = check_gear()
    
    # Equip each gear item using select_menu_option, trying 'Wield' then 'Wear'
    for item in missing_items:
        if item in inventory_items:
            x, y = inventory_items[item]
            # Try 'Wield' first
            print(f"Attempting to equip {item} at inventory coordinates ({x}, {y}) with action 'Wield'...")
            success = select_menu_option(x, y, "Wield")
            if not success:
                # Fall back to 'Wear' if 'Wield' fails
                print(f"'Wield' not available for {item}, trying 'Wear'...")
                success = select_menu_option(x, y, "Wear")
                if not success:
                    print(f"Failed to equip {item} with both 'Wield' and 'Wear'")
                    return False
            print(f"Successfully equipped {item}")
        else:
            print(f"Item {item} not found in inventory after withdrawal")
            return False
    
    bank(withdraw="prayer potion(4)", quantity="all", deposit_inventory=True)

    return True

if __name__ == "__main__":
    print(nmz_bank())