import time
import keyboard
from modules.core.plugin_client import gear, stats, inventory
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.widgets.widget_data import get_all_widget_data 

def check_weapon():
    """
    Check if the currently equipped weapon matches the required weapon based on Attack and Strength levels.
    - Brine Sabre for 40 Attack
    - Granite Hammer for 50 Attack and 50 Strength
    - Dragon Sword for 60 Attack
    If incorrect, opens inventory and clicks the correct weapon if available.

    Returns:
        bool: True if the correct weapon is equipped or successfully equipped, False otherwise.
    """
    # Get player stats
    stats_data = stats()
    if not stats_data or 'data' not in stats_data:
        print("Failed to retrieve player stats.")
        return False

    # Handle different possible stats data structures
    data = stats_data['data']
    attack_level = data.get('Attack', {}).get('level', data.get('attack_level', 0))
    strength_level = data.get('Strength', {}).get('level', data.get('strength_level', 0))
    defence_level = data.get('Defence', {}).get('level', data.get('defence_level', 0))
    print(f"Attack level: {attack_level}, Strength level: {strength_level}, Defence level: {defence_level}")  # Debug

    # Get equipped gear
    gear_data = gear()
    if not gear_data or 'data' not in gear_data:
        print("Failed to retrieve gear data.")
        return False

    # Extract weapon from gear data dictionary
    equipped_weapon = None
    gear_items = gear_data['data']
    if isinstance(gear_items, dict):
        known_weapons = ["Toktz-xil-ak", "Brine Sabre", "Granite Hammer", "Dragon Sword"]
        for item_name in gear_items.keys():
            # Case-insensitive match
            if any(weapon.lower() == item_name.lower() for weapon in known_weapons):
                equipped_weapon = item_name
                break
    print(f"Equipped weapon: {equipped_weapon}")  # Debug

    # Determine required weapon based on levels
    if attack_level >= 60 and strength_level >= 60 and defence_level >= 60:
        required_weapon = "Toktz-xil-ak"
    elif attack_level > 60 and strength_level < 60 and defence_level < 60:
        required_weapon = "Dragon Sword"
    elif attack_level >= 50 and strength_level >= 50:
        required_weapon = "Granite Hammer"
    elif attack_level >= 40:
        required_weapon = "Brine Sabre"
    else:
        required_weapon = "No suitable weapon (level too low)"
        print(f"Levels too low: {required_weapon}")
        return False

    # Check if equipped weapon matches required (case-insensitive)
    if equipped_weapon and equipped_weapon.lower() == required_weapon.lower():
        print(f"Correct weapon equipped: {equipped_weapon}")
        return True

    # If wrong weapon, check if inventory is open before deciding to open
    print(f"Wrong weapon equipped. Expected: {required_weapon}, Got: {equipped_weapon}")
    if not focus_runelite_window():
        print("Failed to focus RuneLite window for inventory check.")
        return False

    # Check if inventory is open (ID 35913793, SpriteID 1026 when open)
    widgets = get_all_widget_data()
    inventory_open = any(widget.get("id") == 35913802 and widget.get("spriteId", -1) == 1030 for widget in widgets)
    if not inventory_open:
        keyboard.press_and_release("f1")
        print("Pressed F1 to open inventory as it was closed.")
        time.sleep(0.1)  # Wait for inventory to open
    else:
        print("Inventory already open, no need to press F1.")

    # Check inventory for required weapon
    inv_data = inventory(item=required_weapon, middle_point=True)
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print(f"{required_weapon} not found in inventory.")
        return False

    # Find and click the required weapon
    for item in inv_data['data']:
        if item.get('name', '').strip().lower() == required_weapon.lower():
            if 'middle_point' in item:
                bounds = item['middle_point']
                canvas_x = bounds['x']
                canvas_y = bounds['y']
                screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                move(screen_x, screen_y, button='left', fast=True)
                print(f"Clicked on {required_weapon} to equip.")
                time.sleep(0.1)  # Wait for equip animation
                return True  # Assume success after click
    print(f"{required_weapon} not found in inventory to equip despite initial check.")
    return False

# Test the function
# while True:
# check_weapon()
    # time.sleep(5)  # Check every 5 seconds