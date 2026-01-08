import random
import keyboard
from typing import Optional, Union, List, Tuple
from modules.core.plugin_client import inventory 
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window 
from modules.widgets.widget import click_widget
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick


def click_inventory(item: str, action: Optional[str] = None, hover_only: bool = False) -> bool:
    """
    Check if the inventory is open and contains the specified item.
    Opens the inventory with F1 if closed, counts the item, and prints its quantity.
    If action is None, left-clicks the first instance.
    If action is provided (e.g., 'Drop'), right-clicks and selects it via context menu.
    Returns True if the item is found, False if none are found and inventory is open.

    Args:
        item (str): The item name to search for (e.g., 'Prayer potion(1)').
        action (Optional[str]): The context menu action (e.g., 'Drop'). Defaults to None (left-click).
        hover_only (bool): If True and action provided, hovers without clicking. Defaults to False.

    Returns:
        bool: True if the item is found, False if none are found and inventory is open.
    """

    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Open inventory if needed
    click_widget('35913802', sprite_id=-1)

    inv_data = inventory()

    # Extract item names and debug
    items = [inv_item.get('name', '').strip().lower() for inv_item in inv_data['data'] if 'name' in inv_item]
    target_item = item.lower().strip()
    count = sum(1 for i in items if i == target_item)

    # Format and print found item count
    if count > 0:
        print(f"{item} x{count}")
        
        # Find the first instance
        first_item = next((inv_item for inv_item in inv_data['data'] if inv_item.get('name', '').strip().lower() == target_item), None)
        if first_item and 'middle_point' in first_item:
            bounds = first_item['middle_point']
            rel_x = bounds['x']  # Relative to window
            rel_y = bounds['y']
            print(bounds, rel_x, rel_y)
            
            if action:
                # Use select_menu_option for context menu action
                result = select_menu_option(rel_x, rel_y, action, hover_only=hover_only)
                return result is not None
            else:
                # Default left-click with random offset
                rl_x, rl_y = runelite_window(0, 0)
                canvas_x = rel_x + rl_x
                canvas_y = rel_y + rl_y
                width = 18
                height = 16
                x, y = canvas_x + random.randint(-width + 2, width - 2), canvas_y + random.randint(-height + 2, height - 2)
                move(x, y, button='left', fast=True, sleep=True)
                return True

    return False

def get_inventory_count(item: str) -> int:
    """
    Returns the number of instances of the specified item in the inventory.

    Args:
        item (str): The item name to count (e.g., 'wild pie').

    Returns:
        int: The count of the item in the inventory.
    """
    inv = inventory().get('data', [])
    return sum(1 for slot in inv if slot.get('name', '').lower() == item.lower())

def check_inventory(item: str) -> tuple[bool, int, tuple[int, int] | None]:
    """
    Checks if the inventory contains the specified item and returns whether it exists, the count, and the random clickpoint of the first occurrence.

    Args:
        item (str): The item name to check for (e.g., 'wild pie').

    Returns:
        tuple[bool, int, tuple[int, int] | None]: (True if item exists, count of the item, (x, y) coordinates of the first item's random clickpoint or None).
    """
    if not focus_runelite_window():
        return False, 0, None

    # Open inventory if needed
    click_widget('35913802', sprite_id=-1)

    inv_data = inventory()

    # Extract item names and find the first matching item's coordinates
    items = inv_data.get('data', [])
    target_item = item.lower().strip()
    count = 0
    clickpoint = None

    for inv_item in items:
        if 'name' in inv_item and inv_item['name'].strip().lower() == target_item:
            count += 1
            if clickpoint is None and 'random_clickpoint' in inv_item:
                clickpoint = (inv_item['random_clickpoint']['x'], inv_item['random_clickpoint']['y'])

    return count > 0, count, clickpoint


def get_inventory_count(item: str) -> int:
    """
    Returns the number of instances of the specified item in the inventory.

    Args:
        item (str): The item name to count (e.g., 'wild pie').

    Returns:
        int: The count of the item in the inventory.
    """
    inv = inventory().get('data', [])
    return sum(1 for slot in inv if slot.get('name', '').lower() == item.lower())

def drop_inventory(item: str, amount: Union[int, str] = 1) -> bool:
    """
    Drops instances of the specified item in the inventory by holding shift and left-clicking each one in a zigzag order.
    Can drop a specific number or all. Drops in batches, waits for a tick, checks if dropped, and retries if necessary.

    Args:
        item (str): The item name to drop (e.g., 'wild pie').
        amount (Union[int, str]): Number of items to drop (int) or 'all' (default: 1).

    Returns:
        bool: True if the requested amount was dropped, False otherwise.
    """
    focus_runelite_window()
    if isinstance(amount, str) and amount.lower() != 'all':
        raise ValueError("Amount must be an integer or 'all'")
    
    initial_count = get_inventory_count(item)
    if initial_count == 0:
        return False
    
    is_all = isinstance(amount, str) and amount.lower() == 'all'
    target_drop = initial_count if is_all else min(int(amount), initial_count)
    dropped_count = 0
    rl_x, rl_y = runelite_window(0, 0)
    
    while dropped_count < target_drop:
        # Get fresh inventory data
        inv = inventory(middle_point=True)
        if not inv or 'data' not in inv:
            break
        items_data = [slot for slot in inv['data'] if slot.get('name', '').lower() == item.lower()]
        if not items_data:
            break
        
        remaining_to_drop = target_drop - dropped_count
        items_data = items_data[:remaining_to_drop]  # Limit to remaining needed
        
        # Compute row and col based on unique middle_points
        unique_x = sorted(set(slot['middle_point']['x'] for slot in items_data))
        unique_y = sorted(set(slot['middle_point']['y'] for slot in items_data))
        col_map = {x: idx for idx, x in enumerate(unique_x)}
        row_map = {y: idx for idx, y in enumerate(unique_y)}
        for slot in items_data:
            slot['col'] = col_map[slot['middle_point']['x']]
            slot['row'] = row_map[slot['middle_point']['y']]
        
        # Sort in zigzag: by block (row//2), then col, then subrow (row%2)
        sorted_items = sorted(items_data, key=lambda d: (d['row'] // 2, d['col'], d['row'] % 2))
        
        keyboard.press('shift')
        for slot in sorted_items:
            point = slot.get('random_clickpoint') or slot.get('middle_point')
            if point:
                screen_x = point['x'] + rl_x
                screen_y = point['y'] + rl_y
                move(screen_x, screen_y, button='left', fast=True, sleep=True)

        keyboard.release('shift')
        
        # Wait for game tick to process the drops
        wait_for_tick()
        
        # Check how many were actually dropped
        current_count = get_inventory_count(item)
        new_dropped = initial_count - current_count
        if new_dropped > dropped_count:
            dropped_count = new_dropped
        else:
            # If no progress, break to avoid infinite loop
            break
    
    return dropped_count >= target_drop

# click_inventory('wild pie', 'eat')
# drop_inventory('wild pie', 'all')
# drop_inventory('wild pie', 18)
# print(check_inventory('wild pie'))