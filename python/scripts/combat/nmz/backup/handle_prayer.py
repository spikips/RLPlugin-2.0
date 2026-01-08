import time
import keyboard
from modules.core.plugin_client import inventory, player
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.utils.wait_for_tick import wait_for_tick
from toggle_prayer import toggle_prayer

def has_prayer_potion():
    """
    Check if there is any Prayer potion in the inventory.
    """
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            print("inventory already open")
            break
    if not tab_open:
        focus_runelite_window()
        keyboard.press_and_release("f1")
        time.sleep(0.1)
        print("inventory not open, pressing f1")

    doses = ['(4)', '(3)', '(2)', '(1)']
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        print("Failed to retrieve inventory data.")
        return False
    return any(any(item.get('name', '').startswith(f'Prayer potion{dose}') for item in inv_data['data']) for dose in doses)

def drink_prayer_potion():
    """
    Drink a dose from the first Prayer potion (lowest slot) in the inventory, regardless of dose.
    Returns True if successful, False otherwise.
    """
    # Check if inventory is open, open with F1 if not
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            print("inventory already open")
            break
    if not tab_open:
        keyboard.press_and_release("f1")
        time.sleep(0.1)
        print("inventory not open, pressing f1")

    # Get inventory data
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for drinking.")
        return False

    # Find the first (lowest index) Prayer potion
    first_potion = None
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            first_potion = inv_item
            break

    if first_potion and 'middle_point' in first_potion:
        bounds = first_potion['middle_point']
        canvas_x = bounds['x']
        canvas_y = bounds['y']
        focus_runelite_window()
        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
        move(screen_x, screen_y, button='left', fast=True)
        print(f"Drank {first_potion.get('name', 'Prayer potion')}")
        wait_for_tick(1)
        return True
    
    print("No Prayer potion found in inventory.")
    return False

def check_prayer_points(drink_threshold=0):
    """
    Check prayer points and drink a Prayer potion if below a random threshold.
    Only toggles 'PROTECT_FROM_MELEE' prayer if a Prayer potion is available.
    Returns True if prayer is managed successfully, False otherwise.
    """
    # Check for prayer potions first
    if not has_prayer_potion():
        print("No Prayer potions in inventory. Skipping prayer activation.")
        return False
    
    # Activate PROTECT_FROM_MELEE prayer
    toggle_prayer('PROTECT_FROM_MELEE', activate=True)
    
    # Check prayer points
    player_data = player(prayer=True).get('data', {})
    current_prayer = player_data.get('prayer', 0)
    
    if current_prayer <= drink_threshold:
        if not drink_prayer_potion():
            print("Failed to drink Prayer potion.")
            return False
        print(f"Prayer points ({current_prayer}) below or at threshold ({drink_threshold}). Drank potion.")
    else:
        print(f"Prayer points ({current_prayer}) above threshold ({drink_threshold}). No drink needed.")
    
    return True

if __name__ == "__main__":
    print(check_prayer_points())