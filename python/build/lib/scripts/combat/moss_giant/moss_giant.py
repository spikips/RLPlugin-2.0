import time
import keyboard
import random
import datetime
import pyautogui
import sys

from moss_giant_bank import moss_giant_bank
from modules.core.plugin_client import player, inventory, game_state, interact_options, tile, stats, gear
from check_inventory import check_inventory 
from check_combat_style import check_combat_style 
from check_weapon import check_weapon 
from check_auto_retaliate import check_auto_retaliate 
from location_check import check_location 
from ground_items import ground_items 
from attack import attack
from toggle_prayer import toggle_prayer 
from check_agro import check_agro 
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move 
from modules.core.window_utils import runelite_window 
from modules.utils.logout import logout_and_break 
from modules.utils.camera import camera 
from modules.utils.wait_for_tick import wait_for_tick
from walk_to_moss_giants import click_minimap_tile

# List of items to loot
items_to_loot = [
    'grimy ranarr weed',
    'snape grass seed',
    'ranarr seed',
    'snapdragon seed',
    'torstol seed',
    'loop half of key',
    'tooth half of key',
    'shield left half',
    'dragon spear',
    'curved bone',
    'long bone',
    'kwuarm seed',
    'mossy key'
]

def has_prayer_potion():
    """
    Check if there is any Prayer potion in the inventory.
    """
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            print("inventory already open")
            break
    if not tab_open:
        pyautogui.press("f1")
        time.sleep(0.1)
        print("inventory not open, pressing f1 - moss_giant.py")

    doses = ['(4)', '(3)', '(2)', '(1)']
    return any(check_inventory(f'Prayer potion{dose}') for dose in doses)

def has_food():
    """
    Check if there is any Wild pie or Half a wild pie in the inventory.
    Clicks on a Wild pie if found, otherwise clicks on a Half a wild pie if found.
    Returns False if neither is found.
    """
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            print("inventory already open")
            break
    if not tab_open:
        pyautogui.press("f1")
        time.sleep(0.1)
        print("inventory not open, pressing f1 - has_food.py")

    # First try to find and click a Wild pie
    if check_inventory("Wild pie", click=True, clicks=3):
        return True
    
    # If no Wild pie, try to find and click a Half a wild pie
    if check_inventory("Half a wild pie", click=True):
        return True
    
    # If neither is found, return False
    print("No Wild pie or Half a wild pie found in inventory.")
    return False

def drink_prayer_potion():
    """
    Drink a dose from the first Prayer potion (lowest slot) in the inventory, regardless of dose.
    Returns True if successful, False otherwise.
    """
    # Get inventory data
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        print("Failed to retrieve inventory data for drinking.")
        return False

    # Find the first (lowest index) Prayer potion
    first_potion = None
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            first_potion = inv_item
            break

    if first_potion and 'middle_point' in first_potion:
        bounds = first_potion['middle_point']
        canvas_x = bounds['x']
        canvas_y = bounds['y']
        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
        move(screen_x, screen_y, button='left', fast=True)
        print(f"Drank {first_potion.get('name', 'Prayer potion')}")
        wait_for_tick(1)
        return True

    print("No Prayer potion found in inventory.")
    return False

def drop_vials():
    """
    Drop all Vials in the inventory using shift-click.
    """
    keyboard.press('shift')
    while check_inventory('Vial', click=True):
        print("Dropped a Vial")
        time.sleep(0.3)  # Small delay between drops
    keyboard.release('shift')

def drop_pie_dish():
    """
    Drop all Vials in the inventory using shift-click.
    """
    keyboard.press('shift')
    while check_inventory('pie dish', click=True):
        print("Dropped a pie dish")
        time.sleep(0.3)  # Small delay between drops
    keyboard.release('shift')

def handle_login_screen(sleep=True):
    """
    Handle if the game is at the login screen by sleeping for a long break and logging back in.
    """
    state = game_state().get('data')
    if state == "LOGIN_SCREEN":
        if sleep:
            sleep_time = random.uniform(35 * 60, 75 * 60)
            print(f"At login screen, sleeping for {sleep_time / 60:.2f} minutes")
            time.sleep(sleep_time)
        # Log back in
        rl_x, rl_y = runelite_window(0, 0)
        move(391 + rl_x, 303 + rl_y, button="left", fast=True, sleep=True)
        time.sleep(random.uniform(0.22, 0.3))
        move(391 + rl_x, 263 + rl_y, button="left", fast=True, sleep=True)
        start_poll = time.time()
        first_logged_in = False
        while time.time() - start_poll < 15:
            state = game_state().get('data')
            if state == 'LOGGED_IN' and not first_logged_in:
                time.sleep(0.4)
                move(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
                time.sleep(0.6)
                first_logged_in = True
                print("Logged back in after unexpected logout")
                return
            time.sleep(0.1)
        print("Login timed out after unexpected logout")
        sys.exit(1)

# def calculate_next_break():
#     global break_time, break_duration, resume_time
#     current_time = time.time()
#     current_elapsed_min = int((current_time - start_time) / 60)
    
#     # Ensure break is at least at current minute or 25
#     min_break_min = max(25, current_elapsed_min)
#     max_break_min = 125
    
#     # Simplified triangular distribution for break minute
#     u = random.random()
#     break_minute = int(min_break_min + (max_break_min - min_break_min + 1) * (1 - (1 - u) ** 0.5))
    
#     # Calculate break time
#     break_time = current_time + (break_minute - current_elapsed_min) * 60
#     # break_time = random.uniform(55, 145) * 60
#     break_duration = random.uniform(35, 55)
#     resume_time = break_time + break_duration * 60
    
#     print(f"Predetermined break at: {datetime.datetime.fromtimestamp(break_time).strftime('%H:%M:%S')} resuming at: {datetime.datetime.fromtimestamp(resume_time).strftime('%H:%M:%S')}")

def calculate_next_break():
    global break_time, break_duration, resume_time
    current_time = time.time()
    
    # Schedule break at a random time between 50 and 145 minutes from now
    break_delay_minutes = random.uniform(50, 145)
    break_time = current_time + break_delay_minutes * 60
    
    # Set break duration between 35 and 55 minutes
    break_duration = random.uniform(35, 55)
    resume_time = break_time + break_duration * 60
    
    print(f"Predetermined break at: {datetime.datetime.fromtimestamp(break_time).strftime('%H:%M:%S')} resuming at: {datetime.datetime.fromtimestamp(resume_time).strftime('%H:%M:%S')}")


def is_in_bad_area():
    player_data = player(location=True).get('data', {})
    loc = player_data.get('location', {})
    px = loc.get('x', 0)
    py = loc.get('y', 0)
    min_x = 2201
    max_x = 2204
    min_y = 3808
    max_y = 3811
    return min_x <= px <= max_x and min_y <= py <= max_y

def select_menu_option(option_text):
    """
    Select a menu option from the right-click menu.
    """
    options = interact_options().get('data', [])
    for opt in options:
        full_option = (opt.get('option', '') + ' ' + opt.get('target', '')).strip().lower()
        if full_option == option_text.lower():
            middle = opt.get('middle_point')
            if middle:
                screen_x, screen_y = runelite_window(middle['x'], middle['y'])
                move(screen_x, screen_y, button='left', fast=True)
                return True
    return False

def check_stats_for_gear():
    stats_data = stats()
    if not stats_data or 'data' not in stats_data:
        print("Failed to retrieve player stats.")
        exit()

    # Handle different possible stats data structures
    data = stats_data['data']
    attack_level = data.get('Attack', {}).get('level', data.get('attack_level', 0))
    strength_level = data.get('Strength', {}).get('level', data.get('strength_level', 0))
    defence_level = data.get('Defence', {}).get('level', data.get('defence_level', 0))

    print(f'attack: {attack_level}, strength: {strength_level}, defence: {defence_level}')
    if attack_level >= 60 and strength_level >= 60 and defence_level >= 60:
        return False
    else:
        return True

def check_gear():
    # Get equipped gear
    gear_data = gear()
    if not gear_data or 'data' not in gear_data:
        print("Failed to retrieve gear data.")
        return False

    # Required gear items
    required_gear = {
        "Toktz-ket-xil",
        "Obsidian platelegs",
        "Berserker necklace",
        "Obsidian helmet",
        "Toktz-xil-ak",
        "Obsidian platebody",
        "Dragon boots"
    }

    # Extract gear items
    gear_items = gear_data['data']
    if not isinstance(gear_items, dict):
        print("Gear data is not a dictionary.")
        return False

    # Check if all required gear is equipped
    equipped_items = set(gear_items.keys())
    missing_gear = required_gear - equipped_items

    if missing_gear:
        print(f"Wrong gear equipped, going bank to equip: {', '.join(missing_gear)}")
        return False
    
    return True

def main(prayer=True):
    """
    Main loop for Moss Giant combat and looting automation.
    """
    global start_time, break_time, break_duration, resume_time, break_pending, drink_threshold

    eat_threshold = None  # Default for non-prayer mode
    drink_threshold = None  # Default for prayer mode

    if prayer:
        drink_threshold = random.randint(1, 27)
    else:
        eat_threshold = random.randint(20, 34)



    start_time = time.time()
    break_pending = False
    calculate_next_break()

    while True:
        # Handle unexpected logouts
        handle_login_screen()

        if prayer:
            prayer = check_stats_for_gear()
            if not prayer:
                moss_giant_bank(prayer=False)

        if not check_location():
            print("Player not in the specified Moss Giant area. Teleporting to castle wars")
            moss_giant_bank(prayer=False)
            continue

        # Ensure correct weapon and combat style
        check_weapon()
        check_combat_style()
        
        if prayer:
            # Ensure Protect from Melee is active
            toggle_prayer('PROTECT_FROM_MELEE', activate=True)

            # Check prayer level and drink if below or at threshold
            player_data = player(prayer=True).get('data', {})
            current_prayer = player_data.get('prayer', 0)
            if current_prayer <= drink_threshold:
                if not has_prayer_potion():
                    print("No Prayer potions left in inventory and prayer is low, banking")
                    toggle_prayer('PROTECT_FROM_MELEE', activate=False)
                    moss_giant_bank()
                if not drink_prayer_potion():
                    print("Failed to drink Prayer potion.")
                else:
                    drop_vials()  # Drop any Vial after drinking
                    drink_threshold = random.randint(1, 27)  # Reset threshold after drink
        
        else:
            player_data = player(health=True).get('data', {})
            current_hp = player_data.get('health', 0)
            print(current_hp)
            if eat_threshold is not None and current_hp <= eat_threshold:
                food = has_food()
                if food:
                    drop_pie_dish()
                    eat_threshold = random.randint(20, 34)
                if not food:
                    moss_giant_bank(prayer=False)


        # Get aggressive Moss Giants (prints status via check_agro)
        aggressive_moss = check_agro('moss giant')

        # Check if there is any aggressive Moss Giant that can reach (regardless of cooldown)
        has_can_reach = any(npc['canReach'] for npc in aggressive_moss)

        current_time = time.time()
        if current_time >= break_time and not break_pending:
            break_pending = True
            print("Break is now pending, waiting for safe moment (no aggressive reachable NPC)")

        if has_can_reach:
            print("Has aggressive Moss Giant that can reach. No action needed.")
            # Check if in bad area and move if safe
            if is_in_bad_area():
                print("Player in bad area (2201-2204,3808-3811), moving to safe tile 2199,3813")
                click_minimap_tile(2199, 3813, 2, 2, right_click=True)
                time.sleep(0.6)  # Wait a tick after moving
        else:
            print("No reachable aggressive Moss Giant. Attacking closest Moss Giant.")
            camera(474, 2011, 200)
            attack('moss giant', tile_radius=10, death_animation=4659)

        # Loot specified items if available
        for item in items_to_loot:
            ground_items(item, tile_radius=10, all=True)

        if break_pending and not has_can_reach:
            print("Safe now (no aggressive reachable NPC), looting and waiting for 25 ticks before break")

            for item in items_to_loot:
                ground_items(item, tile_radius=10, all=True)

            click_minimap_tile(2201, 3810, 0, 0, right_click=True)
            wait_for_tick(25)

            print("Taking predetermined break now")
            logout_and_break(break_duration)
            start_time = time.time()
            calculate_next_break()
            break_pending = False

        time.sleep(0.6)  # Sync with game tick

if __name__ == "__main__":
    handle_login_screen(sleep=False)
    check_auto_retaliate(auto_retaliate=True, leave_combat_tab_open=False)
    prayer = check_stats_for_gear()
    main(prayer=False)