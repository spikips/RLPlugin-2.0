import time
import keyboard
from modules.core.plugin_client import get_active_prayers 
from modules.player_data.prayer.check_prayer_book import check_prayer_spellbook
from modules.widgets.widget_data import get_all_widget_data 
from modules.core.mouse_control import move 
from modules.core.window_utils import runelite_window 

# Dictionary mapping prayer names to widget IDs
# Add more prayers here as needed, e.g., 'PIETY': 12345678
PRAYER_WIDGETS = {
    'PROTECT_FROM_MELEE': 35454999,
    'PROTECT_FROM_RANGE': 35454998,
    'STEEL_SKIN': 35454994
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

def toggle_prayer(prayer_names, activate: bool = True):
    """
    Check if the specified prayer(s) are in the desired state (active or inactive).
    If not, open the prayer book and toggle them by clicking the widgets.

    Args:
        prayer_names (str | tuple[str] | list[str]): Name of the prayer(s) (e.g., 'PROTECT_FROM_MELEE' or ('PROTECT_FROM_RANGE', 'STEEL_SKIN')).
        activate (bool): True to activate, False to deactivate (default: True).

    Returns:
        bool: True if all toggled successfully or already in desired state, False otherwise.
    """
    # Normalize to list for iteration
    if isinstance(prayer_names, str):
        prayer_names = [prayer_names]
    elif not isinstance(prayer_names, (list, tuple)):
        print("Invalid prayer_names type. Must be str, list, or tuple.")
        return False

    # Filter valid prayers
    valid_prayers = [name for name in prayer_names if name in PRAYER_WIDGETS]
    if not valid_prayers:
        print(f"No valid widget IDs found for prayers: {prayer_names}")
        return False

    # Get current active prayers once
    prayer_data = get_active_prayers()
    if not prayer_data or 'data' not in prayer_data:
        print("Failed to retrieve prayer data.")
        return False

    active_prayers = prayer_data['data']
    needs_toggle = []
    all_already_good = True

    for name in valid_prayers:
        is_active = active_prayers.get(name, False)
        if is_active != activate:
            needs_toggle.append(name)
            all_already_good = False
        # else:
            # print(f"{name} is already {'active' if activate else 'inactive'}.")

    if all_already_good:
        # print("All prayers are already in the desired state.")
        return True

    # Open prayer book if needed
    if not check_prayer_spellbook():
        print("Failed to open prayer book.")
        return False

    # Get widget data once
    widgets = get_all_widget_data()
    if not widgets:
        print("Failed to retrieve widget data.")
        return False

    # Create a dict of widget bounds for quick lookup
    widget_bounds = {}
    for widget in widgets:
        wid = widget.get("id")
        if wid in [PRAYER_WIDGETS[name] for name in valid_prayers] and 'bounds' in widget:
            for name, widget_id in PRAYER_WIDGETS.items():
                if wid == widget_id:
                    widget_bounds[name] = widget['bounds']
                    break

    success = True
    for name in needs_toggle:
        widget_id = PRAYER_WIDGETS[name]
        if name not in widget_bounds:
            print(f"Widget bounds for {name} not found.")
            success = False
            continue

        bounds = widget_bounds[name]
        canvas_x = bounds['x'] + bounds['width'] // 2
        canvas_y = bounds['y'] + bounds['height'] // 2
        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
        move(screen_x, screen_y, button='left', fast=True)
        # print(f"Toggled {name} to {'active' if activate else 'inactive'}.")
        keyboard.press_and_release("f1")

    return success

# Examples:
# toggle_prayer("PROTECT_FROM_RANGE")  # Single prayer (backward compatible)
# toggle_prayer(('PROTECT_FROM_RANGE', 'STEEL_SKIN'))  # Multiple prayers