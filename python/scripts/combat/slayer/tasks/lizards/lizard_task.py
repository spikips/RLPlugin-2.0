import time
import random
import sys
import math
import keyboard

from modules.core.plugin_client import player, inventory, game_state, pick, interact_options, gametick, npc, slayer_task_remaining, target_npc
from modules.utils.wait_for_tick import wait_for_tick, wait_for_next_tick
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.utils.camera import camera
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.check_if_in_area import check_if_in_area
from modules.weapon_data.combat_style import combat_style
from modules.player_data.check_run import click_run
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.widgets.widget_data import get_all_widget_data
from modules.utils.select_menu_option import select_menu_option  # New import

# Partial names for attacking (fallback)
LIZARD_PARTIAL_NAMES = ['Small Lizard', 'Lizard', 'Desert Lizard']

# Trigger Ice Cooler when healthRatio <= 4
LOW_HP_HEALTH_RATIO = 4

# Combat animation ID for player attacking
ATTACKING_ANIMATION = 11423

# Lizard area polygon
LIZARD_AREA = [
    "3395,3079,0", "3397,3056,0", "3427,3057,0", "3429,3079,0", "3406,3086,0", "3395,3079,0"
]

def is_attacking():
    p_data = player(animation=True)
    if not p_data or 'data' not in p_data:
        return False
    return p_data['data'].get('animation', -1) == ATTACKING_ANIMATION

def check_attack_status():
    for _ in range(4):
        if is_attacking():
            print("Attack animation detected - still in combat")
            return True
        wait_for_next_tick(1)
    return False

def ensure_prayer_on():
    toggle_prayer('PROTECT_FROM_MELEE', activate=True)

def check_prayer_level():
    p_data = player(prayer=True)
    if not p_data or 'data' not in p_data:
        return 100
    return p_data['data'].get('prayer', 100)

def has_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False
    for item in inv_data['data']:
        name = item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            return True
    return False

def drink_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        return False
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            mp = inv_item['middle_point']
            sx, sy = runelite_window(mp['x'], mp['y'])
            move(sx, sy, fast=True, sleep=True, button='left')
            print(f"Drank {name}")
            wait_for_tick(1)
            return True
    return False

def ensure_inventory_open():
    widgets = get_all_widget_data()
    inventory_tab_id = 35913802
    tab_open = False
    for widget in widgets:
        if widget.get("id") == inventory_tab_id and widget.get("spriteId", -1) == 1030:
            tab_open = True
            break
    if not tab_open:
        print("Opening inventory")
        keyboard.press_and_release("f1")
        time.sleep(0.2)

def get_current_target():
    response = target_npc()
    print(f"[DEBUG] target_npc raw response: {response}")

    if response and 'data' in response and response['data']:
        target = response['data']
        print(f"[DEBUG] Current target: name='{target.get('name')}', id={target.get('id')}, "
              f"index={target.get('index')}, animation={target.get('animation')}, "
              f"healthRatio={target.get('healthRatio')}/{target.get('healthScale')}, "
              f"location={target.get('location')}")
        return target
    else:
        print("[DEBUG] No current target")
        return None

def use_ice_cooler_on_target(target_data: dict):
    """
    Use Ice Cooler via menu option for more human-like behavior
    """
    print("LOW HP (healthRatio <= 4) DETECTED - Using Ice Cooler via menu...")
    ensure_inventory_open()

    # Click Ice Cooler to activate "Use"
    inv_data = inventory()
    cooler_found = False
    if inv_data and 'data' in inv_data:
        for item in inv_data['data']:
            name = item.get('name', '').lower()
            if 'ice cooler' in name:
                mp = item['middle_point']
                sx, sy = runelite_window(mp['x'], mp['y'])
                move(sx, sy, fast=True, sleep=True, button='left')
                print(f"Clicked Ice Cooler: {item.get('name')}")
                cooler_found = True
                break

    if not cooler_found:
        print("Ice Cooler not found in inventory")
        return False

    # Hover over target and select "Use Ice cooler -> Lizard" from menu
    if 'middle_point' in target_data:
        mp = target_data['middle_point']
        target_name = target_data.get('name', 'Lizard')
        expected_action = f"Use Ice cooler -> {target_name}"

        print(f"Selecting menu option: '{expected_action}'")
        success = select_menu_option(mp['x'], mp['y'], expected_action)
        if success:
            print("Ice Cooler used successfully via menu!")
            wait_for_tick(2)
            return True
        else:
            print("Menu selection failed - fallback direct click")
            sx, sy = runelite_window(mp['x'], mp['y'])
            move(sx, sy, fast=True, sleep=True, button='left')
            wait_for_tick(1)
            return True

    print("No middle_point for target")
    return False

def click_target_by_index(target_index: int):
    response = target_npc()
    if response and 'data' in response and response['data']:
        current = response['data']
        if current.get('index') == target_index and 'middle_point' in current:
            mp = current['middle_point']
            sx, sy = runelite_window(mp['x'], mp['y'])
            move(sx, sy, fast=True, sleep=True, button='left')
            print(f"Re-clicked original target (index {target_index})")
            wait_for_tick(2)
            return True
    print(f"Original target index {target_index} lost")
    return False

def handle_login_screen(sleep=True):
    state = game_state().get('data')
    if state == "LOGIN_SCREEN":
        if sleep:
            sleep_time = random.uniform(35 * 60, 75 * 60)
            print(f"At login screen, sleeping {sleep_time / 60:.2f} minutes")
            time.sleep(sleep_time)
        rl_x, rl_y = runelite_window(0, 0)
        move(391 + rl_x, 303 + rl_y, fast=True, sleep=True, button="left")
        time.sleep(random.uniform(0.22, 0.3))
        move(391 + rl_x, 263 + rl_y, fast=True, sleep=True, button="left")
        time.sleep(1)
        print("Logged back in")
        return

def main():
    camera(pitch=400, yaw=200, zoom=300)
    click_run()
    combat_style('aggressive')

    ensure_prayer_on()

    cooler_cooldown = 0
    original_target_index = None
    waiting_for_valid_health = False
    health_wait_ticks = 0

    while True:
        handle_login_screen()

        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            break

        ensure_prayer_on()

        if check_prayer_level() <= 25:
            if has_prayer_potion():
                drink_prayer_potion()
            else:
                print("Prayer low - no potions left")

        current_target = get_current_target()

        if current_target:
            print(f"In combat with {current_target.get('name', 'Unknown')} (ID: {current_target.get('id')})")

            health_ratio = current_target.get('healthRatio', -1)
            current_index = current_target.get('index')

            # Failsafe for aggro switch
            if original_target_index is not None and current_index != original_target_index:
                print(f"AGGRO SWITCH DETECTED! Original {original_target_index} -> New {current_index}")
                if click_target_by_index(original_target_index):
                    continue
                else:
                    print("Failed to switch back - accepting new target")
                    original_target_index = current_index

            # Waiting for valid health after new attack
            if waiting_for_valid_health:
                if health_ratio > -1:
                    print(f"Valid healthRatio {health_ratio} received - monitoring started")
                    waiting_for_valid_health = False
                    health_wait_ticks = 0
                    original_target_index = current_index
                else:
                    health_wait_ticks += 1
                    print(f"Waiting for valid healthRatio ({health_wait_ticks}/5)")
                    if health_wait_ticks >= 5:
                        print("Timeout - re-attacking")
                        waiting_for_valid_health = False
                        original_target_index = None
                        continue
                continue

            # Normal monitoring
            if cooler_cooldown > 0:
                cooler_cooldown -= 1
            elif health_ratio <= LOW_HP_HEALTH_RATIO and health_ratio > -1:
                print(f"HealthRatio {health_ratio} <= {LOW_HP_HEALTH_RATIO} - using Ice Cooler")
                if use_ice_cooler_on_target(current_target):
                    cooler_cooldown = 10
                    original_target_index = None
            else:
                print(f"HealthRatio: {health_ratio}/{current_target.get('healthScale', '?')} (waiting)")
            continue

        # No target - attack new lizard
        print("Not in combat - attacking new lizard")
        success = False
        for name in LIZARD_PARTIAL_NAMES:
            if click_closest_npc(name, 'Attack'):
                success = True
                break

        if not success:
            print("No lizard found - waiting")
            time.sleep(2)
            continue

        waiting_for_valid_health = True
        health_wait_ticks = 0
        original_target_index = None
        cooler_cooldown = 0
        print("Attack initiated - waiting for valid target")
        wait_for_tick(5)


def run():
    main()


if __name__ == "__main__":
    run()
