import time
import random
import pyautogui
from walk_to_moss_giants import walk_to_moss_giant

from modules.utils.banking import bank

from modules.core.plugin_client import inventory, player, gametick, interact_options, bank_items, game_object
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.utils.camera import camera
from modules.widgets.widget_data import get_all_widget_data
from modules.utils.wait_for_tick import wait_for_tick
from check_inventory import check_inventory


def teleport_to_castle_wars():
    # Focus the RuneLite window
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return False

    # Get initial player location
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player location.")
        return False
    initial_location = player_data['data']['location']
    print(f"Initial location: {initial_location}")

    # Ensure inventory is open
    inv_data = inventory(item="ring of dueling")
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data. Attempting to open inventory...")
        pyautogui.press('f1')
        print("Pressed F1 to open inventory.")
        time.sleep(0.05)  # Wait for inventory to open
        inv_data = inventory(item="ring of dueling")
        if not inv_data or 'data' not in inv_data or not inv_data['data']:
            print("Failed to find Ring of Dueling even after opening inventory.")
            return False

    # Get the first Ring of Dueling (any charge)
    ring_item = inv_data['data'][0]  # Assuming it finds at least one
    ring_canvas_x = ring_item.get('random_clickpoint', ring_item.get('middle_point', {'x': 0, 'y': 0}))['x']
    ring_canvas_y = ring_item.get('random_clickpoint', ring_item.get('middle_point', {'x': 0, 'y': 0}))['y']
    ring_screen_x, ring_screen_y = runelite_window(ring_canvas_x, ring_canvas_y)
    print(f"Found Ring of Dueling at canvas ({ring_canvas_x}, {ring_canvas_y}), screen ({ring_screen_x}, {ring_screen_y})")

    # Hover over the ring and right-click
    move(ring_screen_x, ring_screen_y, button='right', fast=True, sleep=True)
    time.sleep(random.uniform(0.1, 0.2))  # Wait for menu to open

    # Get interaction options (menu entries)
    options_data = interact_options()
    if not options_data or 'data' not in options_data:
        print("Failed to retrieve interaction options.")
        return False

    # Find "Rub" option
    rub_option = None
    for opt in options_data['data']:
        if 'rub' in opt.get('option', '').lower():
            rub_option = opt
            break

    if not rub_option:
        print("Rub option not found in menu.")
        return False

    rub_canvas_x = rub_option['middle_point']['x']
    rub_canvas_y = rub_option['middle_point']['y']
    rub_screen_x, rub_screen_y = runelite_window(rub_canvas_x, rub_canvas_y)
    print(f"Hovering over Rub at canvas ({rub_canvas_x}, {rub_canvas_y}), screen ({rub_screen_x}, {rub_screen_y})")

    # Hover over Rub and left-click
    move(rub_screen_x, rub_screen_y, fast=True, sleep=True, button='left')
    # Wait for dialog to open by checking if widget ID 14352385 exists every tick, max 6 ticks
    initial_tick = gametick().get('data', 0)
    max_ticks = 6
    dialog_open = False
    while gametick().get('data', 0) - initial_tick < max_ticks:
        time.sleep(0.6)  # Approximate tick time
        widgets = get_all_widget_data()
        if widgets:
            for widget in widgets:
                if widget.get('id') == 14352385:
                    dialog_open = True
                    break
        if dialog_open:
            break

    if dialog_open:
        pyautogui.press('2')
        print("Pressed '2' to select Castle Wars.")
    else:
        print("Dialog did not open within 6 ticks.")
        return False

    # Check for successful teleport: loop for 12 ticks
    initial_tick = gametick().get('data', 0)
    max_ticks = 12
    success = False
    while gametick().get('data', 0) - initial_tick < max_ticks:
        wait_for_tick()
        current_player_data = player(location=True)
        if not current_player_data or 'data' not in current_player_data or 'location' not in current_player_data['data']:
            continue
        current_location = current_player_data['data']['location']
        if current_location != initial_location:
            print(f"Teleport successful! New location: {current_location}")
            success = True
            break

    if not success:
        print("Teleport failed: Location did not change within 12 ticks.")
        return False

    # Adjust camera after successful teleport
    camera(pitch=494, yaw=1841, zoom=320)
    print("Camera adjusted after teleport.")

    return True

def open_bank():
    # Find bank chest with a broader tile radius
    bank_obj = game_object("bank chest", tile_radius=10, middle_point=True)
    if not bank_obj or 'data' not in bank_obj or not bank_obj['data']:
        print("Failed to find bank chest. Dumping game_object data for debugging:")
        print(bank_obj)
        return False

    bank_item = bank_obj['data'][0]
    bank_canvas_x = bank_item.get('middle_point', {'x': 0, 'y': 0})['x']
    bank_canvas_y = bank_item.get('middle_point', {'x': 0, 'y': 0})['y']
    bank_screen_x, bank_screen_y = runelite_window(bank_canvas_x, bank_canvas_y)
    print(f"Found bank chest at canvas ({bank_canvas_x}, {bank_canvas_y}), screen ({bank_screen_x}, {bank_screen_y})")

    # Hover over the bank to check default action
    print(f"Hovering over bank at {bank_screen_x}, {bank_screen_y} (middle_point from game_object)")
    move(bank_screen_x, bank_screen_y, fast=True, sleep=True)  # Move mouse without clicking
    time.sleep(random.uniform(0.1, 0.2))

    # Get interact options (potential menu)
    options_data = interact_options()
    if not options_data or 'data' not in options_data or not options_data['data']:
        print("No interact options found after hovering")
        return False

    first_option = options_data['data'][0]['option'].lower()
    if 'bank' in first_option or 'use' in first_option:
        # Left-click directly
        print(f"Default action is '{first_option}', left-clicking at {bank_screen_x}, {bank_screen_y}")
        move(bank_screen_x, bank_screen_y, button='left')
    else:
        # Right-click and select 'Bank' or 'Use'
        print(f"Default action is not 'bank' or 'use' ({first_option}), right-clicking")
        move(bank_screen_x, bank_screen_y, button='right')
        time.sleep(random.uniform(0.1, 0.3))
        options_data = interact_options()  # Now with open menu
        if not options_data or 'data' not in options_data:
            print("Failed to retrieve bank chest interaction options after right-click.")
            return False

        bank_option = None
        for opt in options_data['data']:
            option_lower = opt.get('option', '').lower()
            if 'bank' in option_lower or 'use' in option_lower:
                bank_option = opt
                break

        if not bank_option:
            print("Bank/Use option not found in menu.")
            return False

        bank_option_x = bank_option['middle_point']['x']
        bank_option_y = bank_option['middle_point']['y']
        bank_option_screen_x, bank_option_screen_y = runelite_window(bank_option_x, bank_option_y)
        print(f"Selecting 'Bank/Use' from menu at canvas ({bank_option_x}, {bank_option_y}), screen ({bank_option_screen_x}, {bank_option_screen_y}) (middle_point from interact_options)")
        move(bank_option_screen_x, bank_option_screen_y, button='left', fast=True, sleep=True)

    max_attempts = 20  # ~12 seconds (each tick ~0.6s)
    for _ in range(max_attempts):
        bank_data = bank_items()
        if bank_data and 'data' in bank_data and bank_data['data'] is not None and len(bank_data['data']) > 0:
            print("Bank opened successfully.")
            return True
        wait_for_tick()

    print("Failed to open bank after waiting.")
    return False

def perform_banking(prayer):
    if prayer:
        items_to_deposit = [
            'grimy ranarr weed',
            'snape grass seed',
            'ranarr seed',
            'Snapdragon seed',
            'torstol seed',
            'loop half of key',
            'tooth half of key',
            'shield left half',
            'dragon spear',
            'curved bone',
            'Long bone',
            'kwuarm seed',
            'mossy key'
        ]

        items_to_withdraw = [
            ('teleport to house', 'all'),
            ('brine sabre', '1'),
            ('dragon sword', '1'),
            ('granite hammer', '1'),
        ]
    else:
        items_to_withdraw = [
            ('teleport to house', 'all'),
            ('wild pie', 'all')
            ]

    if prayer:
        # Deposit specified items using bank function
        for item in items_to_deposit:
            bank(quantity="all", deposit=item)

        # Withdraw specified items
        for item, quantity in items_to_withdraw:
            bank(withdraw=item, quantity=quantity)
    else:
        # check gear
        withdraw_gear = [
            "Toktz-ket-xil",
            "Obsidian platelegs",
            "Berserker necklace",
            "Obsidian helmet",
            "Toktz-xil-ak",
            "Obsidian platebody",
            "Dragon boots"
        ]

        # Deposit entire inventory
        bank(deposit_inventory=True)

        gear = False
        # Check and withdraw each item
        for item in withdraw_gear:
            result = bank(withdraw=item, quantity='all')
            print(result)
            if result is not False:
                print(f"found {item}")
                gear = True
            
        # close bank, open inventory and equip gear
        if gear:
            pyautogui.press('esc')
            time.sleep(random.uniform(0.22, 0.35))
            for item in withdraw_gear:
                check_inventory(item, click=True)
                time.sleep(random.uniform(0.22, 0.35))
            open_bank()
            bank(deposit_inventory=True)
            
        for item, quantity in items_to_withdraw:
            bank(withdraw=item, quantity=quantity)

        wait_for_tick(2)
        bank(deposit='wild pie', quantity=6)
            

    has_ring = False
    charges = [8, 7, 6, 5, 4, 3, 2, 1]
    for c in charges:
        ring_name = f"ring of dueling({c})"
        ring_inv = inventory(item=ring_name)
        if ring_inv and 'data' in ring_inv and ring_inv['data']:
            has_ring = True
            break

    if not has_ring:
        withdrawn = False
        for c in charges:
            ring_name = f"ring of dueling({c})"
            if bank_items(item=ring_name):
                bank(withdraw=ring_name, quantity="1")
                withdrawn = True
                break
        if not withdrawn:
            print("No ring of dueling available to withdraw.")  

    if prayer:
        # Withdraw all prayer potions
        bank(withdraw="prayer potion(4)", quantity="all")
        if wait_for_tick(2):
            bank(quantity="4", deposit='prayer potion(4)')

    # Close bank with esc
    pyautogui.press('esc')
    print("Closed bank.")
    return True


def moss_giant_bank(prayer):
    if teleport_to_castle_wars():
        if open_bank():
            if perform_banking(prayer=prayer):
                if walk_to_moss_giant():
                    return True
                
# moss_giant_bank(False)