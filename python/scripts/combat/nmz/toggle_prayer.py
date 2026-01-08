import time
import keyboard
from modules.core.plugin_client import get_active_prayers 
from check_prayer_book import check_prayer_spellbook 
from modules.widgets.widget_data import get_all_widget_data 
from modules.core.mouse_control import move 
from modules.core.window_utils import runelite_window 

# Dictionary mapping prayer names to widget IDs
# Add more prayers here as needed, e.g., 'PIETY': 12345678
PRAYER_WIDGETS = {
    'PROTECT_FROM_MELEE': 35454999
}

def check_prayer(prayer_name: str = 'PROTECT_FROM_MELEE'):
    """
    Check if the specified prayer (default: PROTECT_FROM_MELEE) is active.

    Args:
        prayer_name (str): Name of the prayer to check (default: 'PROTECT_FROM_MELEE').

    Returns:
        bool: True if the prayer is active, False otherwise or if data retrieval fails.
    """
    # Get current active prayers
    prayer_data = get_active_prayers()
    if not prayer_data or 'data' not in prayer_data:
        print("Failed to retrieve prayer data.")
        return False

    active_prayers = prayer_data['data']
    is_active = active_prayers.get(prayer_name, False)
    # print(f"{prayer_name} is {'active' if is_active else 'inactive'}.")
    return is_active

def toggle_prayer(prayer_name: str, activate: bool = True):
    """
    Check if the specified prayer is in the desired state (active or inactive).
    If not, open the prayer book and toggle it by clicking the widget.

    Args:
        prayer_name (str): Name of the prayer (e.g., 'PROTECT_FROM_MELEE').
        activate (bool): True to activate, False to deactivate (default: True).

    Returns:
        bool: True if toggled successfully or already in desired state, False otherwise.
    """
    if prayer_name not in PRAYER_WIDGETS:
        print(f"Widget ID for {prayer_name} not found.")
        return False

    # Get current active prayers
    prayer_data = get_active_prayers()
    if not prayer_data or 'data' not in prayer_data:
        print("Failed to retrieve prayer data.")
        return False

    active_prayers = prayer_data['data']
    is_active = active_prayers.get(prayer_name, False)

    # Check if already in desired state
    if is_active == activate:
        print(f"{prayer_name} is already {'active' if activate else 'inactive'}.")
        return True

    # Open prayer book if needed
    if not check_prayer_spellbook():
        print("Failed to open prayer book.")
        return False

    # Get widget data
    widgets = get_all_widget_data()
    if not widgets:
        print("Failed to retrieve widget data.")
        return False

    widget_id = PRAYER_WIDGETS[prayer_name]

    for widget in widgets:
        if widget.get("id") == widget_id:
            if 'bounds' in widget:
                bounds = widget['bounds']
                canvas_x = bounds['x'] + bounds['width'] // 2
                canvas_y = bounds['y'] + bounds['height'] // 2
                screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                move(screen_x, screen_y, button='left', fast=True)
                time.sleep(0.1)  # Delay for toggle
                # print(f"Toggled {prayer_name} to {'active' if activate else 'inactive'}.")
                keyboard.press_and_release("f1")
                return True
            break

    print(f"Widget for {prayer_name} not found.")
    return False

# toggle_prayer("PROTECT_FROM_MELEE")