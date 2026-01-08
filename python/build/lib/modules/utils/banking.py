import time
import json
import random
import keyboard

from modules.core.plugin_client import _default_client, inventory, bank_items, interact_options, gametick
from modules.core.mouse_control import move as mouse, scroll
from modules.core.window_utils import runelite_window

BUTTONS = {
    "itemButton": 786456,
    "notedButton": 786458,
    "searchButton": 786474,
    "depositInvButton": 786476,
    "depositEquipmentButton": 786478,
    "withdraw1Button": 786462,
    "withdraw5Button": 786464,
    "withdraw10Button": 786466,
    "withdrawXButton": 786468,
    "withdrawAllButton": 786470,
    "placeholderButton": 786472
}

SHORTHAND_MAP = {
    "1": "withdraw1Button",
    "5": "withdraw5Button",
    "10": "withdraw10Button",
    "x": "withdrawXButton",
    "all": "withdrawAllButton",
    "item": "itemButton",
    "noted": "notedButton",
    "search": "searchButton",
    "placeholder": "placeholderButton",
    "deposit_inventory": "depositInvButton",
    "deposit_equipment": "depositEquipmentButton"
}

def get_all_widget_data():
    """
    Retrieve data for all visible widgets and their children.
    
    Returns:
        list: List of widget data dictionaries including ID, text, hasOnOpListener, enabled status, and children.
    """
    params = {}  # No specific coordinates, request all widgets
    response = _default_client.send_request("clickWidget", params)
    if not response:
        print("No response from clickWidget request")
        return []

    try:
        data = json.loads(response) if isinstance(response, str) else response
        if isinstance(data, dict) and 'data' in data and 'widgets' in data['data']:
            return data['data']['widgets']
        print(f"Invalid widget data format: {data}")
        return []
    except json.JSONDecodeError as e:
        print(f"Failed to parse widget data: {e}, Raw data: {response}")
        return []

def button(button_input):
    """
    Retrieve the enabled status and random click point for a specified bank button using shorthand input.
    
    Args:
        button_input (str): Shorthand for the button (e.g., '1', '5', '10', 'x', 'all', 'item', 'noted', 'search', 'placeholder').
    
    Returns:
        tuple: (enabled, clickpoint) where:
               - enabled (bool): True if enabled, False if disabled.
               - clickpoint (tuple): (x, y) random click point within bounds, or None if bounds invalid.
    """
    widgets = get_all_widget_data()
    if not widgets:
        print("No widgets found on screen.")
        return None, None

    # Map shorthand to full button name
    button_name = SHORTHAND_MAP.get(button_input, button_input)
    if button_name not in BUTTONS:
        print(f"Invalid button input: {button_input}")
        return False, None

    target_id = BUTTONS[button_name]
    for widget in widgets:
        widget_id = widget.get("id")
        if widget_id == target_id:
            on_op_listener = widget.get("OnOpListener", None)
            bounds = widget.get("bounds", {})
            x = bounds.get("x", 0)
            y = bounds.get("y", 0)
            width = bounds.get("width", 0)
            height = bounds.get("height", 0)
            
            # Debug: Print raw widget data for placeholderButton
            if button_name == "placeholderButton":
                print(f"Raw widget data for {button_name}: {widget}")
                print(f"Widget keys: {list(widget.keys())}")
            
            # Special handling for searchButton: enable if bounds are valid
            if button_name == "searchButton" and width > 0 and height > 0:
                enabled = True
            # Special handling for placeholderButton: check OnOpListener[3]
            elif button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
            else:
                enabled = not widget.get("hasOnOpListener", False)  # True for enabled, False for disabled
            
            # Calculate random click point if bounds are valid
            clickpoint = None
            if width > 0 and height > 0:
                clickpoint = (
                    x + random.randint(1, width - 1),
                    y + random.randint(1, height - 1)
                )
            
            # print(f"{button_name} (ID: {widget_id}): enabled={enabled}, "
            #       f"OnOpListener={on_op_listener}, clickpoint={clickpoint}, "
            #       f"Bounds: X={x}, Y={y}, Width={width}, Height={height}")
            return enabled, clickpoint
    
    # print(f"Button {button_name} (ID: {target_id}) not found in widget data.")
    return False, None

def get_button_status_and_clickpoints():
    """
    Retrieve the status and random click points for specified bank buttons.
    
    Returns:
        dict: Dictionary with button names as keys and values containing:
              - enabled (bool): True if enabled, False if disabled
              - clickpoint (tuple): (x, y) random click point within bounds, or None if bounds invalid
    """
    widgets = get_all_widget_data()
    if not widgets:
        print("No widgets found on screen.")
        return {}

    result = {}
    for widget in widgets:
        widget_id = widget.get("id")
        if widget_id in BUTTONS.values():
            button_name = [name for name, id_val in BUTTONS.items() if id_val == widget_id][0]
            on_op_listener = widget.get("OnOpListener", None)
            bounds = widget.get("bounds", {})
            x = bounds.get("x", 0)
            y = bounds.get("y", 0)
            width = bounds.get("width", 0)
            height = bounds.get("height", 0)
            
            # Special handling for searchButton: enable if bounds are valid
            if button_name == "searchButton" and width > 0 and height > 0:
                enabled = True
            # Special handling for placeholderButton: check OnOpListener[3]
            elif button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
            else:
                enabled = not widget.get("hasOnOpListener", False)  # True for enabled, False for disabled
            
            # Calculate random click point if bounds are valid
            clickpoint = None
            if width > 0 and height > 0:
                clickpoint = (
                    x + random.randint(1, width - 1),
                    y + random.randint(1, height - 1)
                )
            
            result[button_name] = {
                "enabled": enabled,
                "clickpoint": clickpoint
            }
            # print(f"{button_name} (ID: {widget_id}): enabled={enabled}, "
            #       f"OnOpListener={on_op_listener}, clickpoint={clickpoint}, "
            #       f"Bounds: X={x}, Y={y}, Width={width}, Height={height}")

    return result

def monitor_button_status():
    """
    Monitor and print the enabled/disabled status and bounds of specified buttons.
    """
    widgets = get_all_widget_data()
    if not widgets:
        print("No widgets found on screen.")
        return

    for widget in widgets:
        widget_id = widget.get("id")
        if widget_id in BUTTONS.values():
            button_name = [name for name, id_val in BUTTONS.items() if id_val == widget_id][0]
            on_op_listener = widget.get("OnOpListener", None)
            # Special handling for placeholderButton: check OnOpListener[3]
            if button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
                status = "enabled" if enabled else "disabled"
            # Special handling for searchButton: enable if bounds are valid
            elif button_name == "searchButton" and widget.get("bounds", {}).get("width", 0) > 0 and widget.get("bounds", {}).get("height", 0) > 0:
                status = "enabled"
            else:
                status = "enabled" if not widget.get("hasOnOpListener", False) else "disabled"
            bounds = widget.get("bounds", {})
            x = bounds.get("x", 0)
            y = bounds.get("y", 0)
            width = bounds.get("width", 0)
            height = bounds.get("height", 0)
            # print(f"{button_name} (ID: {widget_id}): {status}, "
            #       f"OnOpListener={on_op_listener}, "
            #       f"X: {x}, Y={y}, Width={width}, Height={height}")

def bank(
    deposit="",
    withdraw="",
    search_button=False,
    deposit_inventory=False,
    deposit_equipment=False,
    placeholder=False,
    noted=False,
    unnoted=False,
    amount=None,
    quantity=None
):
    """
    Interact with the bank interface: deposit items, withdraw items, and click buttons.
    
    Args:
        deposit (str): Item name to deposit from inventory (e.g., "sapphire").
        withdraw (str): Item name to withdraw from bank (e.g., "chisel").
        search_button (bool): Click the search button.
        deposit_inventory (bool): Click the deposit inventory button.
        deposit_equipment (bool): Click the deposit equipment button.
        placeholder (bool): Ensure placeholder button is enabled, clicking if disabled.
        noted (bool): Click the noted button (notedButton) if disabled.
        unnoted (bool): Click the unnoted button (itemButton) if disabled.
        amount (str or int): Withdrawal amount ("1", "5", "10", "all", or integer like 14).
        quantity (str): Quantity to set ("1", "5", "10", "x", "all") for deposit/withdraw.
    
    Returns:
        bool: True if all actions succeeded, False otherwise.
    """
    rl_x, rl_y = runelite_window(0, 0)

    # Map quantity/amount to button shorthand
    quantity_map = {
        "1": "1",
        "5": "5",
        "10": "10",
        "x": "x",
        "all": "all"
    }

    # Handle quantity as preset button if it's a string in the map
    if withdraw or deposit:
        if isinstance(quantity, str) and quantity in quantity_map:
            button_shorthand = quantity_map[quantity]
            enabled, clickpoint = button(button_shorthand)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked {button_shorthand} at x={x + rl_x}, y={y + rl_y}")
                time.sleep(random.uniform(0.1, 0.2))
            elif not clickpoint:
                # print(f"Failed to get clickpoint for {button_shorthand}")
                return False

    # Determine effective amount, falling back to quantity if it's a number
    effective_amount = amount
    if effective_amount is None and quantity is not None:
        try:
            effective_amount = int(quantity)
            if effective_amount <= 0:
                print(f"Invalid amount: {effective_amount} must be positive")
                return False
        except ValueError:
            if not isinstance(quantity, str) or quantity not in quantity_map:
                print(f"Invalid quantity: {quantity}")
                return False

    # Handle preset amounts by clicking the corresponding button
    if effective_amount is not None:
        amount_str = str(effective_amount)
        if withdraw and amount_str in ["1", "5", "10", "all"]:
            enabled, clickpoint = button(amount_str)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                # print(f"Clicked withdraw-{amount_str} at x={x + rl_x}, y={y + rl_y}")
                time.sleep(random.uniform(0.1, 0.2))
            elif not clickpoint:
                print(f"Failed to get clickpoint for withdraw-{amount_str}")
                return False

    # Handle placeholder button
    if placeholder:
        enabled, clickpoint = button("placeholder")
        if not enabled and clickpoint:
            x, y = clickpoint
            mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
            print(f"Clicked placeholderButton to enable at x={x + rl_x}, y={y + rl_y}")
            time.sleep(random.uniform(0.1, 0.2))
        elif not clickpoint:
            print("Failed to get clickpoint for placeholderButton")
            return False

    # Handle simple button clicks, only if disabled
    for button_input, flag in [
        ("search", search_button),
        ("deposit_inventory", deposit_inventory),
        ("deposit_equipment", deposit_equipment),
        ("noted", noted),
        ("item", unnoted)
    ]:
        if flag:
            enabled, clickpoint = button(button_input)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked {button_input} at x={x + rl_x}, y={y + rl_y}")
                time.sleep(random.uniform(0.62, 0.75))
            elif not clickpoint:
                print(f"Failed to get clickpoint for {button_input}")
                return False

    # Handle deposit
    if deposit:
        inv_data = inventory(item=deposit)
        print('depositing: ', deposit)
        if not inv_data or 'data' not in inv_data or not inv_data['data']:
            print(f"Item '{deposit}' not found in inventory", inv_data)
            return False
        for item in inv_data['data']:
            if item['name'].lower() == deposit.lower():
                middle_point = item.get("middle_point")
                if middle_point:
                    x, y = middle_point['x'], middle_point['y']
                    if effective_amount is None or str(effective_amount).lower() == "all":
                        # Left-click to deposit all
                        mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                        # print(f"Deposited all {deposit} at x={x + rl_x}, y={y + rl_y}")
                        time.sleep(random.uniform(0.1, 0.2))
                        return True
                    else:
                        # Right-click the item
                        mouse(x + rl_x, y + rl_y, button="right", fast=True, sleep=True)
                        print(f"Right-clicked {deposit} at x={x + rl_x}, y={y + rl_y}")
                        time.sleep(random.uniform(0.1, 0.2))

                        # Get interaction options
                        options = interact_options()
                        if not options or 'data' not in options:
                            print("Failed to get interaction options")
                            return False

                        deposit_opt = None
                        amount_str = str(effective_amount)
                        if amount_str in ["1", "5", "10"]:
                            # Use Deposit-1, Deposit-5, Deposit-10 if applicable
                            target_option = f"deposit-{amount_str}"
                            for opt in options['data']:
                                if opt.get('option', '').lower() == target_option:
                                    deposit_opt = opt
                                    break
                        else:
                            # Use Deposit-X for custom amounts
                            target_option = "deposit-x"
                            for opt in options['data']:
                                if opt.get('option', '').lower() == target_option:
                                    deposit_opt = opt
                                    break

                        if not deposit_opt:
                            print(f"No {target_option.capitalize()} option found in menu")
                            return False

                        middle_point_opt = deposit_opt.get('middle_point', {})
                        if not middle_point_opt:
                            print(f"No middle_point for {target_option.capitalize()} option")
                            return False

                        click_x = middle_point_opt['x'] + random.randint(-20, 20)
                        click_y = middle_point_opt['y'] + random.randint(-6, 6)
                        mouse(click_x + rl_x, click_y + rl_y, button="left", fast=True, sleep=True)
                        print(f"Clicked {target_option.capitalize()} at x={click_x + rl_x}, y={click_y + rl_y}")

                        if amount_str not in ["1", "5", "10"]:
                            # Wait for input widget (ID 10616874) to become visible, checking every tick for max 12 ticks
                            max_ticks = 12
                            tick_response = gametick()
                            if not tick_response or 'data' not in tick_response:
                                print("Failed to get game tick")
                                return False
                            start_tick = tick_response['data']
                            current_tick = start_tick
                            input_open = False

                            while current_tick - start_tick < max_ticks:
                                widgets = get_all_widget_data()
                                for widget in widgets:
                                    if widget.get("id") == 10616874:
                                        input_open = True
                                        break
                                if input_open:
                                    break

                                # Wait for next tick
                                while True:
                                    tick_response = gametick()
                                    if tick_response and 'data' in tick_response:
                                        new_tick = tick_response['data']
                                        if new_tick > current_tick:
                                            current_tick = new_tick
                                            break
                                    time.sleep(0.05)

                            if not input_open:
                                print("Timeout waiting for input dialog widget (ID 10616874) to open.")
                                return False

                            # Type amount and press Enter
                            keyboard.write(str(effective_amount))
                            time.sleep(random.uniform(0.1, 0.2))
                            keyboard.press_and_release("enter")
                            print(f"Typed amount {effective_amount} and pressed Enter")
                        time.sleep(random.uniform(0.1, 0.2))
                        return True
                else:
                    print(f"No middle_point for {deposit} in inventory")
                    return False
        print(f"Item '{deposit}' not found in inventory data")
        return False

    # Handle withdraw
    if withdraw:
        if find_items_bank(withdraw, effective_amount):
            # print(f"Withdrew {withdraw}")
            return True
        else:
            print(f"Failed to withdraw {withdraw}")
            return False

    return True

def find_items_bank(item_name, amount=None):
    """
    Find and click an item in the bank interface, scrolling if needed. Avoids moving the mouse to a random
    position if 8 or more scrolls are required in the same direction.

    Args:
        item_name (str): Name of the item to find.
        amount (int, optional): Custom amount to withdraw using right-click Withdraw-X.

    Returns:
        bool: True if item was found and clicked, False otherwise.
    """
    max_attempts = 5
    attempt = 0
    total_scrolls_up = 0
    total_scrolls_down = 0

    while attempt < max_attempts:
        # Get bank items data
        bank_data = bank_items()
        item_found = False

        # Search for the item
        for item in bank_data['data']:
            if item['name'].lower() == item_name.lower():
                if item['quantity'] == 0:
                    print(f"Item '{item_name}' found but has quantity 0.")
                    return False
                x = item['middle_point']['x']
                y = item['middle_point']['y']
                item_found = True

                # Check if y is within acceptable range (90 <= y <= 290)
                if 90 <= y <= 290:
                    # Move to item and click
                    rl_x, rl_y = runelite_window(0, 0)
                    if amount is None or str(amount).lower() in ["1", "5", "10", "all"]:
                        mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                        print(f"Clicked {item_name} at x={x + rl_x}, y={y + rl_y}")
                        return True
                    else:
                        # Right-click the item
                        mouse(x + rl_x, y + rl_y, button="right", fast=True, sleep=True)
                        print(f"Right-clicked {item_name} at x={x + rl_x}, y={y + rl_y}")
                        time.sleep(random.uniform(0.1, 0.2))

                        # Get interaction options
                        options = interact_options()
                        if not options or 'data' not in options:
                            print("Failed to get interaction options")
                            return False

                        withdraw_x_opt = None
                        for opt in options['data']:
                            if opt.get('option', '').lower() == 'withdraw-x':
                                withdraw_x_opt = opt
                                break

                        if not withdraw_x_opt:
                            print("No Withdraw-X option found in menu")
                            return False

                        middle_point = withdraw_x_opt.get('middle_point', {})
                        if not middle_point:
                            print("No middle_point for Withdraw-X option")
                            return False

                        click_x = middle_point['x'] + random.randint(-20, 20)
                        click_y = middle_point['y'] + random.randint(-6, 6)
                        mouse(click_x + rl_x, click_y + rl_y, button="left", fast=True, sleep=True)
                        print(f"Clicked Withdraw-X at x={click_x + rl_x}, y={click_y + rl_y}")

                        # Wait for input widget (ID 10616874) to become visible, checking every tick for max 12 ticks
                        max_ticks = 12
                        tick_response = gametick()
                        if not tick_response or 'data' not in tick_response:
                            print("Failed to get game tick")
                            return False
                        start_tick = tick_response['data']
                        current_tick = start_tick
                        input_open = False

                        while current_tick - start_tick < max_ticks:
                            widgets = get_all_widget_data()
                            for widget in widgets:
                                if widget.get("id") == 10616874:
                                    input_open = True
                                    break
                            if input_open:
                                break

                            # Wait for next tick
                            while True:
                                tick_response = gametick()
                                if tick_response and 'data' in tick_response:
                                    new_tick = tick_response['data']
                                    if new_tick > current_tick:
                                        current_tick = new_tick
                                        break
                                time.sleep(0.05)

                        if not input_open:
                            print("Timeout waiting for input dialog widget (ID 10616874) to open.")
                            return False

                        # Type amount and press Enter
                        keyboard.write(str(amount))
                        time.sleep(random.uniform(0.1, 0.2))
                        keyboard.press_and_release("enter")
                        print(f"Typed amount {amount} and pressed Enter")
                        time.sleep(random.uniform(0.1, 0.2))
                        return True
                else:
                    # Update scroll counters
                    if y < 90:
                        total_scrolls_up += 4
                    else:  # y > 290
                        total_scrolls_down += 4

                    # Move mouse only if < 8 total scrolls in one direction
                    if total_scrolls_up < 8 and total_scrolls_down < 8:
                        random_x = random.randint(100, 400)
                        random_y = random.randint(100, 280)
                        rl_x, rl_y = runelite_window(0, 0)
                        mouse(random_x + rl_x, random_y + rl_y, button=None, fast=True, sleep=True)
                        print(f"Moved mouse to x={random_x + rl_x}, y={random_y + rl_y} before scrolling")

                    # Scroll based on y position
                    if y < 90:
                        print(f"Scrolling up 4 times (y={y}, total up={total_scrolls_up})")
                        for _ in range(4):
                            scroll(1)  # 1 scrolls up
                    else:  # y > 290
                        print(f"Scrolling down 4 times (y={y}, total down={total_scrolls_down})")
                        for _ in range(4):
                            scroll(-1)  # -1 scrolls down

                    break  # Exit for loop to recheck bank items

        if not item_found:
            # print(f"Item '{item_name}' not found in bank.")
            return False

        attempt += 1
        time.sleep(0.6)  # Delay between attempts for stability

    print(f"Failed to find '{item_name}' with quantity > 0 and y in range 90-290 after {max_attempts} attempts.")
    return False

# bank(quantity="all", deposit='Long bone')
# bank(quantity="all", deposit='snapdragon seed')
# bank(quantity="3", withdraw='prayer potion(4)')
# bank(quantity="4", deposit='prayer potion(4)')