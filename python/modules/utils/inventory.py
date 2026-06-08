import random
import keyboard
import time
import re
from typing import Optional, Union, List, Tuple
from modules.core.plugin_client import inventory 
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window 
from modules.widgets.widget import click_widget, check_widget
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick


def click_inventory(item: str, action: Optional[str] = None, hover_only: bool = False, fast: bool = False) -> bool:
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
    
    inv_data = check_widget('35913795', sprite_id=-1)
    if inv_data:
        for _ in range(3):
            print("Inventory not open, attempting to open it.")
            # click_widget('35913795', sprite_id=1030, rand_x=10, rand_y=10)
            keyboard.press_and_release('f1')

            for _ in range(60):
                inv_data = inventory()
                if inv_data and 'data' in inv_data:
                    break
                time.sleep(0.01)
            
            if inv_data and 'data' in inv_data:
                break
    else:
        inv_data = inventory()


    # Helper to normalize item names from plugin (strip tags, normalize spacing and parens)
    def _normalize_name(s: str) -> str:
        if not s:
            return ''
        s = re.sub(r'<[^>]+>', '', s)  # strip any color/html tags
        s = s.replace('\xa0', ' ')
        s = re.sub(r"\s+", ' ', s).strip()
        # Ensure a single space before parentheses, which some sources may omit
        s = re.sub(r"\s*\(", ' (', s)
        return s.lower()

    # Extract and normalize item names
    items = [_normalize_name(inv_item.get('name', '')) for inv_item in inv_data['data'] if 'name' in inv_item]
    target_item = _normalize_name(item)
    count = sum(1 for i in items if i == target_item)

    # Format and print found item count
    if count > 0:
        print(f"{item} x{count}")
        
    # Find the first instance (normalized comparison)
    first_item = next((inv_item for inv_item in inv_data['data'] if _normalize_name(inv_item.get('name', '')) == target_item), None)
    if first_item and 'middle_point' in first_item:
        bounds = first_item['middle_point']
        rel_x = bounds['x']  # Relative to window
        rel_y = bounds['y']

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
            move(x, y, button='left', fast=fast, sleep=fast)
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


    for _ in range(3):
        click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=10, rand_y=10)


    for _ in range(60):
        inv_data = inventory()
        if inv_data and 'data' in inv_data:
            break
        time.sleep(0.01)
    else:
        exit("no inventory data after attempting to open inventory")


    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False, 0, None

    # Helper to normalize names (keep same logic as click_inventory)
    def _normalize_name(s: str) -> str:
        if not s:
            return ''
        s = re.sub(r'<[^>]+>', '', s)
        s = s.replace('\xa0', ' ')
        s = re.sub(r"\s+", ' ', s).strip()
        s = re.sub(r"\s*\(", ' (', s)
        return s.lower()

    # Extract item names and find the first matching item's coordinates
    items = inv_data.get('data', [])
    target_item = _normalize_name(item)
    count = 0
    clickpoint = None

    for inv_item in items:
        if 'name' in inv_item and _normalize_name(inv_item['name']) == target_item:
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

def drop_inventory(item: str, amount: Union[int, str] = 1, fast: bool = False) -> bool:
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
                move(screen_x, screen_y, button='left', fast=fast, sleep=fast)

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

def click_inventory_sequence(items: List[str], action: Optional[str] = None, delay: float = random.uniform(0.04, 0.08), fast: bool = False) -> bool:
    """
    Clicks items in the inventory in the specified sequence. For sequences with multiple identical
    items (e.g., ['short vine', 'short vine']), it fetches all instances once, then clicks each
    unique slot in order (e.g., vine in slot 1, then slot 2). This ensures different instances
    are targeted, even if the game hasn't processed the first click yet. Refreshes inventory
    data between different items in the sequence.

    Args:
        items (List[str]): Sequence of item names to click in order (e.g., ['short vine', 'short vine']).
        action (Optional[str]): The context menu action (e.g., 'Drop'). Defaults to None (left-click).
        delay (float): Optional delay (seconds) between clicks to allow game updates. Defaults to 0.6s.

    Returns:
        bool: True if all items were successfully clicked, False otherwise.
    """
    success = True
    i = 0
    while i < len(items):
        current_item = items[i]
        # Group consecutive identical items to click all at once
        instances_to_click = []
        while i < len(items) and items[i] == current_item:
            instances_to_click.append(current_item)
            i += 1
        
        # Fetch fresh inventory data
        if not focus_runelite_window():
            print("Failed to focus RuneLite window.")
            success = False
            break
        
        inv_data = inventory()
        if not inv_data or 'data' not in inv_data:
            print("Failed to open inventory.")
            success = False
            break
        
        # Normalize helper (reuse from click_inventory)
        def _normalize_name(s: str) -> str:
            if not s:
                return ''
            s = re.sub(r'<[^>]+>', '', s)
            s = s.replace('\xa0', ' ')
            s = re.sub(r"\s+", ' ', s).strip()
            s = re.sub(r"\s*\(", ' (', s)
            return s.lower()
        
        target_item = _normalize_name(current_item)
        matching_items = [inv_item for inv_item in inv_data['data'] 
                          if 'name' in inv_item and _normalize_name(inv_item['name']) == target_item]
        
        num_needed = len(instances_to_click)
        if len(matching_items) < num_needed:
            print(f"Only {len(matching_items)} {current_item} available, but {num_needed} requested.")
            success = False
            break
        
        # Click each matching item in inventory order (different slots)
        for j in range(num_needed):
            inv_item = matching_items[j]
            if 'middle_point' not in inv_item:
                print(f"No click point for {current_item} instance {j+1}.")
                success = False
                break
            
            bounds = inv_item['middle_point']
            rel_x = bounds['x']
            rel_y = bounds['y']
            
            if action:
                # Use select_menu_option for context menu action
                result = select_menu_option(rel_x, rel_y, action)
                if result is None:
                    print(f"Failed to perform action '{action}' on {current_item} instance {j+1}.")
                    success = False
            else:
                # Default left-click with random offset
                rl_x, rl_y = runelite_window(0, 0)
                canvas_x = rel_x + rl_x
                canvas_y = rel_y + rl_y
                width = 18
                height = 16
                x, y = (canvas_x + random.randint(-width + 2, width - 2), 
                        canvas_y + random.randint(-height + 2, height - 2))
                move(x, y, button='left', fast=fast, sleep=fast)
                print(f"Clicked {current_item} instance {j+1} (left-click).")
            
            if delay > 0:
                time.sleep(delay)
        
        if not success:
            break
    
    return success

def check_inventory_space():
    inv_data = inventory()
    return(len(inv_data['data']))


def is_inventory_full() -> bool:
    """
    Returns True if the inventory is completely full (28 occupied slots).
    Based on how the inventory() plugin works in your framework:
    - 'data' contains only occupied slots (items with quantity > 0).
    - Empty slots are not included in the list.
    - OSRS inventory has exactly 28 slots, so len == 28 means full.
    """
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        print("Failed to retrieve inventory data")
        return False  # Or True if you prefer to assume full on error
    
    occupied_slots = len(inv_data['data'])
    print(f"Inventory slots used: {occupied_slots}/28")
    
    return occupied_slots == 28


def free_inventory_slots() -> int:
    """
    Returns the number of free inventory slots (28 minus occupied).
    Useful for checking if there's room for specific loot.
    """
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return 0
    
    occupied = len(inv_data['data'])
    return max(0, 28 - occupied)


# print(is_inventory_full())
# prints something like Inventory slots used: 16/28
# returns False when not full, True when full


# click_inventory_sequence(['short vine', 'short vine'])
# click_inventory_sequence(['iron axe', 'hammer', 'knife'])
# click_inventory('wild pie', 'eat')
# drop_inventory('wild pie', 'all')
# drop_inventory('wild pie', 18)
# print(check_inventory('wild pie'))
# print(get_inventory_count('dragon bones'))