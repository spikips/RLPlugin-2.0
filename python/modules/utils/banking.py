import time
import json
import random
import keyboard

from modules.core.plugin_client import _default_client, inventory, bank_items, interact_options, gametick
from modules.core.mouse_control import move as mouse, scroll
from modules.core.window_utils import runelite_window
from modules.utils.wait_for_tick import wait_for_tick

BUTTONS = {
    "notedButton": 786451,  # spriteId 179 = noted enabled, 170 = item mode
    "searchButton": 786468,
    "depositInvButton": 786473,
    "depositEquipmentButton": 786475,
    "withdraw1Button": 786455,
    "withdraw5Button": 786457,
    "withdraw10Button": 786459,
    "withdrawXButton": 786461,
    "withdrawAllButton": 786463,
    "placeholderButton": 786466
}

SHORTHAND_MAP = {
    "1": "withdraw1Button",
    "5": "withdraw5Button",
    "10": "withdraw10Button",
    "x": "withdrawXButton",
    "all": "withdrawAllButton",
    "noted": "notedButton",
    "search": "searchButton",
    "placeholder": "placeholderButton",
    "deposit_inventory": "depositInvButton",
    "deposit_equipment": "depositEquipmentButton"
}

def get_all_widget_data():
    params = {}
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
    widgets = get_all_widget_data()
    if not widgets:
        print("No widgets found on screen.")
        return None, None

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
            sprite_id = widget.get("spriteId", -1)

            if button_name == "notedButton":
                enabled = sprite_id == 179  # True = noted mode enabled
            elif button_name == "searchButton" and width > 0 and height > 0:
                enabled = True
            elif button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
            else:
                enabled = not widget.get("hasOnOpListener", False)

            clickpoint = None
            if width > 0 and height > 0:
                clickpoint = (
                    x + random.randint(1, width - 1),
                    y + random.randint(1, height - 1)
                )

            return enabled, clickpoint

    return False, None

def get_button_status_and_clickpoints():
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
            sprite_id = widget.get("spriteId", -1)

            if button_name == "notedButton":
                enabled = sprite_id == 179
            elif button_name == "searchButton" and width > 0 and height > 0:
                enabled = True
            elif button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
            else:
                enabled = not widget.get("hasOnOpListener", False)

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

    return result

def monitor_button_status():
    widgets = get_all_widget_data()
    if not widgets:
        print("No widgets found on screen.")
        return

    for widget in widgets:
        widget_id = widget.get("id")
        if widget_id in BUTTONS.values():
            button_name = [name for name, id_val in BUTTONS.items() if id_val == widget_id][0]
            on_op_listener = widget.get("OnOpListener", None)
            sprite_id = widget.get("spriteId", -1)
            bounds = widget.get("bounds", {})

            if button_name == "notedButton":
                status = "enabled (noted)" if sprite_id == 179 else "disabled (item mode)"
            elif button_name == "searchButton" and bounds.get("width", 0) > 0 and bounds.get("height", 0) > 0:
                status = "enabled"
            elif button_name == "placeholderButton":
                enabled = isinstance(on_op_listener, list) and len(on_op_listener) > 3 and on_op_listener[3] == 0
                status = "enabled" if enabled else "disabled"
            else:
                status = "enabled" if not widget.get("hasOnOpListener", False) else "disabled"

            x = bounds.get("x", 0)
            y = bounds.get("y", 0)
            width = bounds.get("width", 0)
            height = bounds.get("height", 0)
            print(f"{button_name} (ID: {widget_id}): {status}, SpriteID: {sprite_id}, "
                  f"X: {x}, Y: {y}, Width: {width}, Height: {height}")

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
    rl_x, rl_y = runelite_window(0, 0)

    quantity_map = {
        "1": "1",
        "5": "5",
        "10": "10",
        "x": "x",
        "all": "all"
    }

    # Preset quantity buttons (1,5,10,x,all)
    if withdraw or deposit:
        if isinstance(quantity, str) and quantity in quantity_map:
            button_shorthand = quantity_map[quantity]
            enabled, clickpoint = button(button_shorthand)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked preset quantity button: {button_shorthand}")
                time.sleep(random.uniform(0.1, 0.2))

    # Determine effective amount for custom X
    effective_amount = amount
    if effective_amount is None and quantity is not None:
        try:
            effective_amount = int(quantity)
            if effective_amount <= 0:
                print(f"Invalid amount: {effective_amount} must be positive")
                return False
        except ValueError:
            pass

    # Preset amount buttons for withdraw (1,5,10,all) when amount is a string matching
    if effective_amount is not None:
        amount_str = str(effective_amount)
        if withdraw and amount_str in ["1", "5", "10", "all"]:
            enabled, clickpoint = button(amount_str)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked withdraw preset: {amount_str}")
                time.sleep(random.uniform(0.1, 0.2))

    # Handle noted/unnoted toggle (single button now)
    if noted or unnoted:
        enabled, clickpoint = button("noted")
        if enabled is None or clickpoint is None:
            print("Failed to detect noted toggle button")
            return False
        desired_not_ed = noted  # If both True, prioritizes noted
        if bool(enabled) != desired_not_ed:
            x, y = clickpoint
            mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
            print(f"Toggled to {'noted' if desired_not_ed else 'item'} mode")
            time.sleep(random.uniform(0.1, 0.2))

    # Placeholder button
    if placeholder:
        enabled, clickpoint = button("placeholder")
        if not enabled and clickpoint:
            x, y = clickpoint
            mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
            print("Enabled placeholders")
            time.sleep(random.uniform(0.1, 0.2))

    # Simple button clicks
    for button_input, flag in [
        ("search", search_button),
        ("deposit_inventory", deposit_inventory),
        ("deposit_equipment", deposit_equipment)
    ]:
        if flag:
            enabled, clickpoint = button(button_input)
            if not enabled and clickpoint:
                x, y = clickpoint
                mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                print(f"Clicked {button_input}")
                time.sleep(random.uniform(0.62, 0.75))

    # Deposit logic
    if deposit:
        inv_data = inventory(item=deposit)
        if not inv_data or 'data' not in inv_data or not inv_data['data']:
            print(f"Item '{deposit}' not found in inventory")
            return False

        for item in inv_data['data']:
            if item['name'].lower() == deposit.lower():
                middle_point = item.get("middle_point")
                if not middle_point:
                    print("No middle_point for deposit item")
                    return False

                x, y = middle_point['x'], middle_point['y']
                if effective_amount is None or str(effective_amount).lower() == "all":
                    mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                    print(f"Deposited all {deposit}")
                    time.sleep(random.uniform(0.1, 0.2))
                    return True
                else:
                    mouse(x + rl_x, y + rl_y, button="right", fast=True, sleep=True)
                    time.sleep(random.uniform(0.1, 0.2))

                    options = interact_options()
                    if not options or 'data' not in options:
                        print("Failed to get interaction options")
                        return False

                    target_option = f"deposit-{str(effective_amount)}" if str(effective_amount) in ["1", "5", "10"] else "deposit-x"
                    deposit_opt = next((opt for opt in options['data'] if opt.get('option', '').lower() == target_option), None)
                    if not deposit_opt:
                        print(f"No {target_option} option found")
                        return False

                    mp = deposit_opt.get('middle_point', {})
                    if not mp:
                        return False

                    for _ in range(5):
                        click_x = mp['x'] + random.randint(-10, 10)
                        click_y = mp['y']
                        mouse(click_x + rl_x, click_y + rl_y, button="left", fast=True, sleep=True)
                        print(f"Selected {target_option}")

                        if target_option == "deposit-x":
                            # Wait for input dialog
                            max_ticks = 12
                            start_tick = gametick().get('data', 0)
                            current_tick = start_tick
                            input_open = False
                            while current_tick - start_tick < max_ticks:
                                widgets = get_all_widget_data()
                                if any(w.get("id") == 10616874 for w in widgets):
                                    input_open = True
                                    break
                                while gametick().get('data', 0) <= current_tick:
                                    time.sleep(0.05)
                                current_tick = gametick().get('data', 0)

                            if input_open:
                                keyboard.write(str(effective_amount))
                                time.sleep(random.uniform(0.1, 0.2))
                                keyboard.press_and_release("enter")
                                print(f"Entered amount {effective_amount}")
                        time.sleep(random.uniform(0.1, 0.2))
                        return True
                    
        print(f"Item '{deposit}' not found in inventory data")
        return False

    # Withdraw logic
    if withdraw:
        return find_items_bank(withdraw, effective_amount)

    return True

def find_items_bank(item_name, amount=None):
    max_attempts = 5
    attempt = 0
    total_scrolls_up = 0
    total_scrolls_down = 0

    while attempt < max_attempts:
        bank_data = bank_items()
        if not bank_data or 'data' not in bank_data:
            attempt += 1
            time.sleep(0.6)
            continue

        item_found = False
        for item in bank_data['data']:
            if item['name'].lower() == item_name.lower():
                if item.get('quantity', 0) == 0:
                    print(f"Item '{item_name}' has quantity 0")
                    return False

                middle_point = item.get('middle_point')
                if not middle_point:
                    continue

                x = middle_point['x']
                y = middle_point['y']
                item_found = True

                if 90 <= y <= 290:
                    rl_x, rl_y = runelite_window(0, 0)

                    if amount is None or str(amount).lower() in ["1", "5", "10", "all"]:
                        mouse(x + rl_x, y + rl_y, button="left", fast=True, sleep=True)
                        print(f"Withdrew {item_name} (preset/left-click)")
                        return True
                    else:
                        mouse(x + rl_x, y + rl_y, button="right", fast=True, sleep=True)
                        time.sleep(random.uniform(0.1, 0.2))

                        options = interact_options()
                        if not options or 'data' not in options:
                            return False

                        withdraw_opt = next((opt for opt in options['data'] if opt.get('option', '').lower() == 'withdraw-x'), None)
                        if not withdraw_opt:
                            print("No Withdraw-X option")
                            return False

                        mp = withdraw_opt.get('middle_point', {})
                        if not mp:
                            return False

                        click_x = mp['x'] + random.randint(-10, 10)
                        click_y = mp['y']
                        mouse(click_x + rl_x, click_y + rl_y, button="left", fast=True, sleep=True)
                        print("Selected Withdraw-X")

                        # Wait for input dialog
                        max_ticks = 12
                        start_tick = gametick().get('data', 0)
                        current_tick = start_tick
                        input_open = False
                        while current_tick - start_tick < max_ticks:
                            widgets = get_all_widget_data()
                            if any(w.get("id") == 10616874 for w in widgets):
                                input_open = True
                                break
                            while gametick().get('data', 0) <= current_tick:
                                time.sleep(0.05)
                            current_tick = gametick().get('data', 0)

                        if input_open:
                            keyboard.write(str(amount))
                            time.sleep(random.uniform(0.1, 0.2))
                            keyboard.press_and_release("enter")
                            print(f"Entered withdraw amount {amount}")
                        time.sleep(random.uniform(0.1, 0.2))
                        return True
                else:
                    # Scroll handling
                    if y < 90:
                        total_scrolls_up += 4
                    else:
                        total_scrolls_down += 4

                    if total_scrolls_up < 8 and total_scrolls_down < 8:
                        random_x = random.randint(100, 400)
                        random_y = random.randint(100, 280)
                        rl_x, rl_y = runelite_window(0, 0)
                        mouse(random_x + rl_x, random_y + rl_y, button=None, fast=True, sleep=True)

                    if y < 90:
                        for _ in range(4):
                            scroll(1)  # up
                    else:
                        for _ in range(4):
                            scroll(-1)  # down
                    break

        if not item_found:
            print(f"Item '{item_name}' not found in bank")
            return False

        attempt += 1
        time.sleep(0.6)

    print(f"Failed to locate '{item_name}' after {max_attempts} attempts")
    return False

# bank(quantity="all", deposit="amulet of glory")
# Example test calls (uncomment to test)
# bank(quantity="1", withdraw='dwarven rock cake')
# bank(quantity="all", deposit='snapdragon seed')
# bank(quantity="3", withdraw='prayer potion(4)')

# bank(quantity="4", deposit='prayer potion(4)')
# print(bank(quantity="all", withdraw="dragon bones", deposit_inventory=True))