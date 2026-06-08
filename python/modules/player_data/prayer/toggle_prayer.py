import time
import keyboard
from modules.core.plugin_client import get_active_prayers, player 
from modules.player_data.prayer.check_prayer_book import check_prayer_spellbook
from modules.widgets.widget import click_widget
from modules.widgets.widget_data import get_all_widget_data 
from modules.core.mouse_control import move 
from modules.core.window_utils import focus_runelite_window, runelite_window
from scripts.combat.moss_giant.ground_items import wait_for_next_tick 

# Dictionary mapping prayer names to widget IDs
# Add more prayers here as needed, e.g., 'PIETY': 12345678
PRAYER_WIDGETS = {
    'PROTECT_FROM_MELEE': 35454999,
    'PROTECT_FROM_RANGE': 35454998,
    'PROTECT_FROM_MAGIC': 35454997,
    'STEEL_SKIN': 35454994,
    'PIETY': 35455011

}

def toggle_prayer(prayer_names, activate: bool = True):
    focus_runelite_window()
    """
    Check if the specified prayer(s) are in the desired state (active or inactive).
    If not, open the prayer book and toggle them by clicking the widgets.

    NEW FEATURE:
    If activate=True and we have 0 prayer points, skip everything immediately
    (no opening prayer book, no clicks, no wasted time).
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

    # === NEW CHECK: Prayer points when activating ===
    if activate:
        try:
            pl_data = player()
            if pl_data and 'data' in pl_data:
                prayer_points = pl_data['data'].get('prayer', 0)
                if prayer_points <= 0:
                    print(f"No prayer points remaining ({prayer_points}). Skipping activation of {valid_prayers}.")
                    return False
                else:
                    print(f"Prayer points available: {prayer_points} - proceeding.")
            else:
                print("Warning: Could not fetch player data for prayer points check.")
        except Exception as e:
            print(f"Could not check prayer points: {e}. Proceeding anyway (rare).")

    # === Original logic (unchanged) ===
    for _ in range(5):
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
            else:
                print(f"{name} is already {'active' if activate else 'inactive'}.")

        if all_already_good:
            return True

        # Open prayer book if needed
        for i in range(5):
             if check_prayer_spellbook():
                 break
             wait_for_next_tick()
             if i == 4:
                 print("Failed to open prayer spellbook after 5 attempts.")
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

        for name in needs_toggle:
            widget_id = PRAYER_WIDGETS[name]
            if name not in widget_bounds:
                print(f"Widget bounds for {name} not found.")
                continue

            bounds = widget_bounds[name]
            canvas_x = bounds['x'] + bounds['width'] // 2
            canvas_y = bounds['y'] + bounds['height'] // 2
            screen_x, screen_y = runelite_window(canvas_x, canvas_y)
            move(screen_x, screen_y, button='left')
            keyboard.press_and_release("f1")
        
        continue

    print(f"Failed to toggle prayers to desired state after 5 attempts.")
    return False


def disable_all_prayer():
    """
    Disables all active prayers, but ONLY if at least one prayer is currently enabled.
    Skips the entire click sequence if no prayers are on (fast & safe).
    """
    # === QUICK CHECK: Do we even need to do anything? ===
    prayer_data = get_active_prayers()
    if prayer_data and 'data' in prayer_data:
        active_prayers = prayer_data['data']
        if not any(active_prayers.values()):
            print("No prayers currently active - skipping disable.")
            return True

    print("At least one prayer is active - disabling all...")

    # === Original disable sequence (unchanged) ===
    for i in range(5):
        if click_widget('10485780', action='Activate quick-prayers', hidden=False, right_click=False,
                        rand_x=5, rand_y=5, clicks=2, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()

    # 2
    for i in range(3):
        if click_widget('10485780', action='Deactivate quick-prayers', hidden=False, right_click=False,
                        rand_x=5, rand_y=5, clicks=1, sleep_interval=(0, 0)):
            return True
        wait_for_next_tick()

    print("Failed to disable prayers after attempts.")
    return False


# toggle_prayer('PIETY', activate=True)