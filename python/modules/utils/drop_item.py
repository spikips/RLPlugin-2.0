import random
import time
import keyboard
from modules.core.mouse_control import move
from modules.core.plugin_client import inventory
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.utils.loot import wait_for_next_tick
from modules.widgets.widget import check_widget, click_widget


def open_inventory_tab():
    if not focus_runelite_window():
        return False

    widget_id = '35913795'
    if check_widget(widget_id, sprite_id=-1):
        print("Inventory not open, attempting to open it.")
        for _ in range(3):
            click_widget(widget_id, sprite_id=1030, rand_x=20, rand_y=20)
            for _ in range(60):
                inv_data = inventory()
                if inv_data and 'data' in inv_data:
                    return True
                time.sleep(0.01)
    else:
        return True
    return False


def drop_item(item_name: str, exact_match: bool = True) -> bool:
    """
    Shift-click drops ONE occurrence of the specified item (requires RuneLite 'Shift click to drop items' enabled).
    - Opens inventory tab first to ensure it's visible.
    - Matching is now CASE-INSENSITIVE by default.
    - If exact_match=True (default): requires exact name match (ignoring case).
    - If exact_match=False: allows partial/substring match (e.g., 'nature' would match 'Nature rune').
    - For stackable items: drops ONE item per call (repeat if you want to drop more).
    - Returns True if dropped, False if item not found.
    """
    # Always ensure inventory tab is open
    open_inventory_tab()

    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("No inventory data available")
        return False

    item_lower = item_name.strip().lower()

    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        name_lower = name.lower()

        # Case-insensitive comparison
        if (exact_match and name_lower == item_lower) or \
           (not exact_match and item_lower in name_lower):
            mp = inv_item['middle_point']
            sx, sy = runelite_window(mp['x'], mp['y'])

            # Hold shift
            keyboard.press('shift')
            time.sleep(random.uniform(0.05, 0.12))

            # Move and left-click
            move(sx, sy, fast=True, sleep=False, button='left')

            # Small hold after click
            time.sleep(random.uniform(0.08, 0.18))
            keyboard.release('shift')

            # Wait for drop to register
            wait_for_next_tick(1)

            print(f"Shift-dropped: {name}")
            return True

    print(f"No matching item found to drop: {item_name}")
    return False

# drop_item('grimy ranarr weed')