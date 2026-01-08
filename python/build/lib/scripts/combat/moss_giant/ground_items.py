import time
import random
from typing import Dict
from modules.core.plugin_client import player, pick, interact_options, gametick, inventory
from modules.core.mouse_control import move, get_cursor_pos
from modules.core.window_utils import runelite_window

def wait_for_next_tick(num_ticks: int = 1):
    """
    Wait for a specified number of game ticks.
    """
    current_tick = gametick().get('data', 0)
    print(f"Current tick: {current_tick}")
    target_tick = current_tick + num_ticks
    while True:
        time.sleep(0.05)
        next_tick = gametick().get('data', 0)
        if next_tick >= target_tick:
            print(f"Reached tick: {next_tick}")
            break

def wait_for_player_to_stop_moving():
    """
    Wait until the player stops moving (animation idle or no path).
    """
    max_wait_ticks = 10  # Max ~6s
    current_tick = gametick().get('data', 0)
    end_tick = current_tick + max_wait_ticks
    last_position = None

    while gametick().get('data', 0) < end_tick:
        player_data = player(location=True, animation=True)
        if player_data and 'data' in player_data:
            loc = player_data['data'].get('location', {})
            animation = player_data['data'].get('animation', -1)
            current_position = (loc.get('x'), loc.get('y'))
            if last_position == current_position and animation == -1:  # Idle and position stable
                print("Player has stopped moving.")
                return True
            last_position = current_position
        time.sleep(0.1)
    print("Timeout waiting for player to stop moving.")
    return False

def wait_for_item_in_inventory(item_name: str, initial_quantity: int = 0):
    """
    Wait until the item appears in the inventory or quantity increases for stackable items.
    """
    max_wait_ticks = 2  # Reduced to 2 ticks (~1.2s max)
    current_tick = gametick().get('data', 0)
    end_tick = current_tick + max_wait_ticks
    item_name_lower = item_name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()  # Ignore doses

    while gametick().get('data', 0) < end_tick:
        inv_data = inventory(item=item_name)
        if inv_data and 'data' in inv_data:
            for inv_item in inv_data['data']:
                inv_item_name_lower = inv_item.get('item', '').lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()
                if inv_item_name_lower == item_name_lower:
                    inv_quantity = inv_item.get('quantity', 0)
                    if inv_quantity > initial_quantity:
                        print(f"Item {item_name} detected in inventory with quantity {inv_quantity}.")
                        return True
        time.sleep(0.05)  # Fast polling
    print(f"Timeout waiting for {item_name} in inventory. Assuming success and proceeding.")
    return True  # Assume success on timeout to avoid blocking

def clean_target_name(target: str) -> str:
    """
    Remove color tags (e.g., <col=ff9040>) and quantity suffixes from the target name.
    """
    if target.startswith('<col='):
        end_idx = target.find('>')
        if end_idx != -1:
            target = target[end_idx + 1:]
    # Remove ' x N' suffixes
    if ' x ' in target:
        target = target.split(' x ')[0]
    return target.strip()

def can_pick_item(item_name: str) -> bool:
    """
    Check if the inventory has space to pick up the item.
    Returns True if there's space or if the item can stack with an existing one.
    """
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        print("Failed to retrieve inventory data.")
        return False

    items = inv_data['data']
    occupied_slots = len(items)
    item_name_lower = item_name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()

    has_item = any(
        inv_item.get('item', '').lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip() == item_name_lower
        for inv_item in items
    )

    if occupied_slots < 28 or has_item:
        return True
    else:
        print("Inventory full, cannot pick up item.")
        return False

def ground_items(item_name: str, tile_radius: int = 10, all: bool = True):
    """
    Pick up all ground items matching the given name within the specified tile radius, sorted by distance.
    Handles cases where the item is stacked under other items by right-clicking and selecting the appropriate option.
    Hovers first to check if left-click is possible.
    Waits until item appears in inventory after pickup.
    Failsafe for when player is on the loot tile: retry up to 3 times with 2 tick waits.
    If walking to tile was required, wait 2 ticks before next item.
    Ensures item is picked up before moving to next by waiting for player to stop moving if distance >0.
    Rechecks ground items and re-hovers after walking, pickup, and 2 ticks wait.
    """
    capitalized_item = ' '.join(word.capitalize() for word in item_name.split())

    picked_count = 0

    while True:
        # Get current player location
        player_data = player(location=True)
        if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
            print("Failed to retrieve player location.")
            return

        loc = player_data['data']['location']
        player_x = loc['x']
        player_y = loc['y']

        # Retrieve ground items matching the item name within the radius
        ground_data = pick(player_x, player_y, size=tile_radius, item=item_name)
        if not ground_data or 'data' not in ground_data or not ground_data['data'].get('items'):
            return

        items = ground_data['data'].get('items', [])

        # Sort items by distance to player
        def get_distance(item: Dict) -> float:
            tile_x = item.get('tile', {}).get('x', 0)
            tile_y = item.get('tile', {}).get('y', 0)
            return (tile_x - player_x) ** 2 + (tile_y - player_y) ** 2

        items.sort(key=get_distance)

        # Process only the closest item, then refetch
        item = items[0]
        if 'tile' not in item:
            print("Skipping item due to missing 'tile'.")
            continue

        tile_x = item['tile']['x']
        tile_y = item['tile']['y']
        distance = abs(tile_x - player_x) + abs(tile_y - player_y)
        initial_quantity = 0
        inv_data = inventory(item=item_name)
        if inv_data and 'data' in inv_data:
            for inv_item in inv_data['data']:
                inv_item_name_lower = inv_item.get('item', '').lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()
                if inv_item_name_lower == item_name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip():
                    initial_quantity = inv_item.get('quantity', 0)
                    break
        print(f"Initial quantity of {item_name}: {initial_quantity}")

        if not can_pick_item(item_name):
            print(f"Cannot pick up {item_name} due to full inventory.")
            return

        picked_up = False
        is_player_on_tile = (tile_x == player_x and tile_y == player_y)
        max_loops = 3 if is_player_on_tile else 1
        loop_count = 0

        while loop_count < max_loops and not picked_up:
            loop_count += 1
            print(f"Pickup attempt {loop_count}/{max_loops}")

            mp = item['middle_point']
            rl_x, rl_y = runelite_window(mp['x'], mp['y'])
            print(f"Adjusted middle point screen coords: ({rl_x}, {rl_y})")

            # Human-like mouse movement to hover over the item
            move(rl_x, rl_y, fast=True, sleep=True)
            time.sleep(random.uniform(0.05, 0.1))  # Short sleep for hover to register

            # Get interaction options on hover (top-left menu text)
            hover_menu_data = interact_options()
            print("Hover menu data:", hover_menu_data)

            hover_menu_entries = []
            if hover_menu_data and 'data' in hover_menu_data:
                hover_menu_entries = hover_menu_data['data'] if isinstance(hover_menu_data['data'], list) else []

            print("Hover menu entries:", hover_menu_entries)

            # Check if top option is 'Take [item]'
            is_top_take = False
            if hover_menu_entries:
                top_entry = hover_menu_entries[0]
                if 'option' in top_entry and 'target' in top_entry:
                    option_lower = top_entry['option'].lower()
                    target_clean = clean_target_name(top_entry['target']).lower()
                    if option_lower.startswith('take') and item_name.lower() in target_clean:
                        is_top_take = True

            if is_top_take:
                print("Top option is Take, left-clicking.")
                move(button='left', fast=True, sleep=True)
            else:
                print("Top option not Take or no hover data, right-clicking.")
                # Right-click to open menu
                move(button='right', fast=True, sleep=False)
                time.sleep(random.uniform(0.05, 0.1))  # Short sleep after right-click

                # Get interaction options (menu entries)
                menu_data = interact_options()
                print("Menu data after right-click:", menu_data)

                menu_entries = []
                if menu_data and 'data' in menu_data:
                    menu_entries = menu_data['data'] if isinstance(menu_data['data'], list) else []

                print("Menu entries:", menu_entries)

                # Find the entry for "Take [item_name]"
                target_entry = None
                for entry in menu_entries:
                    if 'option' in entry and 'target' in entry:
                        option_lower = entry['option'].lower()
                        target_clean = clean_target_name(entry['target']).lower()
                        if option_lower.startswith('take') and item_name.lower() in target_clean:
                            target_entry = entry
                            break

                if target_entry:
                    if 'middle_point' in target_entry:
                        mp = target_entry['middle_point']
                        rl_x, rl_y = runelite_window(mp['x'], mp['y'])
                        click_x = rl_x + random.randint(-10, 10)
                        click_y = rl_y + random.randint(-3, 3)
                        print(f"Calculated click position using middle_point: ({click_x}, {click_y})")
                        # Move and left-click on the menu entry
                        move(click_x, click_y, fast=True, button='left', sleep=True)
                    else:
                        print("No middle_point in target entry.")
                        continue
                else:
                    # Move away without clicking
                    curr_x, curr_y = get_cursor_pos()
                    move(curr_x + random.randint(100, 200), curr_y, fast=False)
                    continue

            # Wait until item appears in inventory
            picked_up = wait_for_item_in_inventory(item_name, initial_quantity)

            if picked_up:
                print(f"Successfully picked up {item_name}.")
                picked_count += 1
            else:
                print(f"Failed to detect {item_name} in inventory after attempt {loop_count}.")
                if is_player_on_tile:
                    print("Player on tile failsafe: Waiting 2 ticks before retry.")
                    wait_for_next_tick(3)

        if not picked_up and loop_count == max_loops:
            print(f"Exceeded max loops ({max_loops}) for {item_name}. Proceeding to next.")

        if not picked_up and not is_player_on_tile:
            # Poll every tick until player is on the tile
            max_poll_ticks = 20
            current_tick = gametick().get('data', 0)
            end_tick = current_tick + max_poll_ticks
            reached_tile = False
            while gametick().get('data', 0) < end_tick:
                player_data = player(location=True)
                if player_data and 'data' in player_data:
                    loc = player_data['data']['location']
                    if loc['x'] == tile_x and loc['y'] == tile_y:
                        print("walked to the tile, proceeding to the next item")
                        reached_tile = True
                        break
                time.sleep(0.05)
            if not reached_tile:
                print("Timeout waiting to reach the tile.")

        if distance > 0:
            print("Walking was required, waiting 2 ticks before next item.")
            wait_for_next_tick(3)

        if not all:
            return

# if __name__ == "__main__":
#     ground_items('Vial')
#     ground_items('Prayer potion(4)')