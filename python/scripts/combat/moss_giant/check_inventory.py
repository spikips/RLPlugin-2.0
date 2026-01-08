import time
import keyboard
from modules.core.plugin_client import inventory 
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window 
from modules.utils.wait_for_tick import wait_for_tick

def check_inventory(item: str, click: bool = False, clicks=1):
    """
    Check if the inventory is open and contains the specified item.
    Opens the inventory with F1 if closed, counts the item, and prints its quantity.
    Optionally clicks on the first instance of the item.
    Returns True if the item is found, False if none are found and inventory is open.

    Args:
        item (str): The item name to search for (e.g., 'Prayer potion(1)').
        click (bool): If True, clicks on the first instance of the item (default: False).

    Returns:
        bool: True if the item is found, False if none are found and inventory is open.
    """

    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Get current inventory data and debug
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data. Attempting to open inventory...")
        # Attempt to open inventory with F1
        keyboard.press_and_release("f1")
        print("Pressed F1 to open inventory.")  # Debug
        time.sleep(0.05)  # Wait 50 ms for inventory to open
        
        # Retry inventory check up to 3 times
        for _ in range(3):
            inv_data = inventory()
            if inv_data and 'data' in inv_data and inv_data['data']:
                break
            time.sleep(0.1)  # Wait between retries
        else:
            print("Inventory still inaccessible after opening attempts.")
            return False

    # Extract item names and debug
    items = [inv_item.get('name', '').strip().lower() for inv_item in inv_data['data'] if 'name' in inv_item]
    target_item = item.lower().strip()
    count = sum(1 for i in items if i == target_item)

    # Format and print found item count
    if count > 0:
        print(f"{item} x{count}")
        
        # Optionally click on the first instance
        if click and inv_data['data']:
            first_item = next((inv_item for inv_item in inv_data['data'] if inv_item.get('name', '').strip().lower() == target_item), None)
            if first_item and 'middle_point' in first_item:
                bounds = first_item['middle_point']
                canvas_x = bounds['x']
                canvas_y = bounds['y']
                screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                for _ in range(0, clicks):
                    move(screen_x, screen_y, button='left', fast=True, sleep=True)
                    print(f"Clicked on {item}")
                    if clicks > 1:
                        wait_for_tick(ticks=2)
        return True
    else:
        print(f"No {item} found in inventory.")
        return False

# Test the function
# while True:
# check_inventory('wild pie', click=True, clicks=2)
#     time.sleep(5)  # Check every 5 seconds