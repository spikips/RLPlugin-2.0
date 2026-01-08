# Modified check_combat_style.py
import json
import os
import pyautogui
from modules.core.plugin_client import gear
from modules.core.window_utils import focus_runelite_window
from modules.widgets.widget import click_widget_child, check_widget
WEAPON_DATA_FILE = os.path.join(os.path.dirname(__file__), "weapon_data.json") 

def load_weapon_data():
    try:
        with open(WEAPON_DATA_FILE, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"Error: {WEAPON_DATA_FILE} not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {WEAPON_DATA_FILE}.")
        return None

weapon_data = load_weapon_data()

def get_weapon_category(weapon_name):
    if not weapon_data or 'weapons' not in weapon_data:
        return None
    # Normalize to lowercase for matching
    return weapon_data['weapons'].get(weapon_name.lower(), None)

def get_style_widget_id(category, desired_style):
    if not weapon_data or 'categories' not in weapon_data:
        return None
    cat_data = weapon_data['categories'].get(category.lower(), None)
    if not cat_data or 'styles' not in cat_data:
        return None
    style_data = cat_data['styles'].get(desired_style.lower(), None)
    if not style_data:
        return None
    return style_data.get('id', None)

def combat_style(desired_style):
    # Ensure RuneLite window is focused
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    print(f"Desired combat style: {desired_style}")

    # Determine weapon type (category) based on equipped weapon using dynamic data
    gear_data = gear()
    if not gear_data or 'data' not in gear_data:
        print("Failed to retrieve gear data. Defaulting to blunt weapon.")
        weapon_category = "blunt"
    else:
        equipped_items = gear_data['data']
        weapon_category = "blunt"  # Default
        weapon_name = None
        for item_name in equipped_items.keys():
            # Assume the key is the weapon name; adjust if gear() returns differently
            category = get_weapon_category(item_name)
            if category:
                weapon_name = item_name
                weapon_category = category
                break
        if weapon_name:
            print(f"Detected weapon: {weapon_name}, Category: {weapon_category}")
        else:
            print("No recognized weapon detected. Defaulting to blunt.")

    # New: Get the widget ID for the desired style in this category
    widget_id = get_style_widget_id(weapon_category, desired_style)
    if widget_id is None:
        print(f"No widget ID found for style '{desired_style}' in category '{weapon_category}'.")
        return False

    # Check if the combat tab is open (from weapons_info.txt: Id 35913791, SpriteId 1026 when open)
    if not check_widget('35913791', sprite_id=1026):
        print("Combat tab not open. Opening it...")
        pyautogui.press("f3")

    print(f'{str(widget_id)}')
    # Check if the style is already selected (sprite_id=1154 enabled)
    if check_widget(f'{str(widget_id)}', sprite_id=1154):
        print(f"Style '{desired_style}' already selected.")
        return True

    # Click to select (target when disabled, sprite_id=1145)
    if click_widget_child(str(widget_id), sprite_id=1154, child_index=4):
        print(f"Successfully switched to '{desired_style}' style.")
        return True
    else:
        print(f"Failed to click widget for '{desired_style}'.")
        return False

# combat_style('defence')