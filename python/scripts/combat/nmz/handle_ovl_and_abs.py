import time
import keyboard
from modules.core.plugin_client import inventory, player, varbit
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.utils.wait_for_tick import wait_for_tick
import gc  # Import garbage collector

def has_absorption_potion(inv_data):
    """
    Check if there is any Absorption potion in the inventory.

    Args:
        inv_data (dict): Inventory data from plugin_client.inventory().

    Returns:
        bool: True if an Absorption potion is found, False otherwise.
    """
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for Absorption check.")
        return False

    doses = ['(4)', '(3)', '(2)', '(1)']
    found = False
    for item in inv_data['data']:
        name = item.get('name', '').strip().replace(' ', '')  # Normalize spaces
        # print(f"Checking item: {item.get('name', 'Unknown')} (normalized: {name})")  # Debug
        if any(name.startswith(f'Absorption{dose}') for dose in doses):
            found = True
            break
    del inv_data  # Explicitly delete to free memory
    gc.collect()  # Force GC
    return found

def has_overload(inv_data):
    """
    Check if there is any Overload potion in the inventory.

    Args:
        inv_data (dict): Inventory data from plugin_client.inventory().

    Returns:
        bool: True if an Overload potion is found, False otherwise.
    """
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for Overload check.")
        return False

    doses = ['(4)', '(3)', '(2)', '(1)']
    found = False
    for item in inv_data['data']:
        name = item.get('name', '').strip().replace(' ', '')  # Normalize spaces
        # print(f"Checking item: {item.get('name', 'Unknown')} (normalized: {name})")  # Debug
        if any(name.startswith(f'Overload{dose}') for dose in doses):
            found = True
            break
    del inv_data  # Explicitly delete
    gc.collect()
    return found

def drink_absorption_potion():
    """
    Drink a dose from the first Absorption potion (lowest slot) in the inventory, regardless of dose.
    Returns True if successful, False otherwise.
    """
    # Check if inventory is open, open with F1 if not
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            # print("Inventory already open")
            break
    if not tab_open:
        focus_runelite_window()
        keyboard.press_and_release("f1")
        time.sleep(0.1)
        print("Inventory not open, pressing f1")

    # Get inventory data
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for drinking.")
        return False

    # Find the first (lowest index) Absorption potion
    first_potion = None
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip().replace(' ', '')
        if name.startswith('Absorption('):
            first_potion = inv_item
            break

    if first_potion and 'middle_point' in first_potion:
        bounds = first_potion['middle_point']
        canvas_x = bounds['x']
        canvas_y = bounds['y']
        focus_runelite_window()
        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
        move(screen_x, screen_y, button='left', fast=True)
        print(f"Drank {first_potion.get('name', 'Absorption potion')}")
        wait_for_tick(1)
        del inv_data, widgets, first_potion  # Clean up
        gc.collect()
        return True
    
    print("No Absorption potion found in inventory.")
    del inv_data, widgets
    gc.collect()
    return False

def drink_overload():
    """
    Drink a dose from the first Overload potion (lowest slot) in the inventory, regardless of dose.
    Returns True if successful, False otherwise.
    """
    # Check if inventory is open, open with F1 if not
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            # print("Inventory already open")
            break
    if not tab_open:
        focus_runelite_window()
        keyboard.press_and_release("f1")
        time.sleep(0.1)
        print("Inventory not open, pressing f1")

    # Get inventory data
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for drinking.")
        return False

    # Find the first (lowest index) Overload
    first_potion = None
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip().replace(' ', '')
        if name.startswith('Overload('):
            first_potion = inv_item
            break

    if first_potion and 'middle_point' in first_potion:
        bounds = first_potion['middle_point']
        canvas_x = bounds['x']
        canvas_y = bounds['y']
        focus_runelite_window()
        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
        move(screen_x, screen_y, button='left', fast=True)
        print(f"Drank {first_potion.get('name', 'Overload')}")
        wait_for_tick(1)
        del inv_data, widgets, first_potion
        gc.collect()
        return True
    
    print("No Overload found in inventory.")
    del inv_data, widgets
    gc.collect()
    return False

def check_absorption_and_overload(absorption_threshold=50):
    """
    Check absorption points and overload status, drinking potions as needed.
    Drinks 4 doses of Absorption potion if points are below the threshold.
    Drinks Overload if the effect is not active (Varbit 3955 = 0).
    Returns True if both are managed successfully, False otherwise.
    """
    success = True

    # Check if inventory is open, open with F1 if not
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            # print("Inventory already open")
            break
    if not tab_open:
        focus_runelite_window()
        keyboard.press_and_release("f1")
        time.sleep(0.1)
        print("Inventory not open, pressing f1")

    # Get inventory data once for both checks
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        print("Failed to retrieve inventory data in check_absorption_and_overload.")
        del widgets
        gc.collect()
        return False
    # print(f"Inventory data: {inv_data['data']}")  # Debug

    # Check for potions
    has_absorption = has_absorption_potion(inv_data)
    has_overload_potion = has_overload(inv_data)
    
    # Check absorption points (Varbit 3956 tracks NMZ absorption points)
    if has_absorption:
        absorption_points = varbit(3956)
        if absorption_points is None:
            print("Failed to retrieve absorption points (Varbit 3956).")
            success = False
        elif absorption_points <= absorption_threshold:
            doses_drank = 0
            for i in range(4):  # Attempt to drink 4 doses
                if not has_absorption_potion(inv_data):
                    # print(f"Stopped at {doses_drank} doses: No more Absorption potions in inventory.")
                    success = False
                    break
                if not drink_absorption_potion():
                    print(f"Failed to drink Absorption potion dose {doses_drank + 1}.")
                    success = False
                    break
                doses_drank += 1
                # print(f"Absorption points ({absorption_points}) below or at threshold ({absorption_threshold}). Drank dose {doses_drank}.")
                if i < 3:  # Wait for tick between doses, except after the last one
                    wait_for_tick(1)
                    # Refresh inventory data after drinking
                    inv_data = inventory()
                    if not inv_data or 'data' not in inv_data:
                        print("Failed to retrieve updated inventory data.")
                        success = False
                        break
                    # Update absorption points after each dose
                    absorption_points = varbit(3956)
                    if absorption_points is None:
                        print("Failed to retrieve updated absorption points (Varbit 3956).")
                        success = False
                        break
            if doses_drank == 4:
                print(f"Successfully drank 4 doses of Absorption potion.")
        else:
            print(f"Absorption points ({absorption_points}) above threshold ({absorption_threshold}). No drink needed.")
    else:
        # print("No Absorption potions in inventory.")
        success = False

    # Check overload status (Varbit 3955: 0 = inactive, >0 = active)
    if has_overload_potion:
        overload_active = varbit(3955)
        if overload_active is None:
            print("Failed to retrieve overload status (Varbit 3955).")
            success = False
        elif overload_active == 0:
            if not drink_overload():
                print("Failed to drink Overload.")
                success = False
            else:
                print("Overload not active (Varbit 3955 = 0). Drank Overload.")
        else:
            print(f"Overload already active (Varbit 3955 = {overload_active}). No drink needed.")
    else:
        print("No Overload potions in inventory.")
        success = False

    del inv_data, widgets  # Clean up
    gc.collect()
    return success

if __name__ == "__main__":
    print(check_absorption_and_overload())