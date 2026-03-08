import time
import random
import sys
import math

from modules.core.plugin_client import player, inventory, game_state, pick, interact_options, gametick, npc, slayer_task_remaining
from modules.utils.wait_for_tick import wait_for_tick
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

# great kourend - teleport to wintertodt -> minecart to kingstown 
# "twisted banshee"
# inv: ear muffs, 1 prayer pot, no cannon
# stand at 1623, 9989 tile
# pickup rune dagger, rune full helm, battlestaff, air battlestaff, rune med helm, mystic gloves (dark),
# snapdragon seed, torstol seed, snape grass seed, ancient shard, dark totem base, dark totem middle,
# dark totem top


# Valuable items to loot from Twisted Banshees
items_to_loot = [
    'rune dagger',
    'rune full helm',
    'battlestaff',
    'air battlestaff',
    'rune med helm',
    'mystic gloves (dark)',
    'snapdragon seed',
    'torstol seed',
    'snape grass seed',
    'ancient shard',
    'dark totem base',
    'dark totem middle',
    'dark totem top'
]

# Safe spot tile (walkway in Catacombs of Kourend)
TARGET_TILE = (1623, 9989, 0)

# Twisted Banshee area polygon
TWISTED_BANSHEE_AREA = [
    "1620,9987,0", "1620,9995,0", "1627,9995,0", "1627,9987,0"
]

# Twisted Banshee NPC ID
TWISTED_BANSHEE_ID = 7272

# Combat animation IDs
ATTACKING_ANIMATION = 11423
BANSHEE_DEATH_ANIMATION = 1524

def get_player_position():
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return 0, 0, 0
    loc = p_data['data'].get('location', {})
    return loc.get('x', 0), loc.get('y', 0), loc.get('plane', 0)

def normalize_item_name(name: str) -> str:
    return name.lower().replace('(4)', '').replace('(3)', '').replace('(2)', '').replace('(1)', '').strip()

def clean_target_name(target: str) -> str:
    if target.startswith('<col='):
        end_idx = target.find('>')
        if end_idx != -1:
            target = target[end_idx + 1:]
    if ' x ' in target:
        target = target.split(' x ')[0]
    return target.strip()

def can_pick_item(item_name: str) -> bool:
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False
    items = inv_data['data']
    occupied_slots = len(items)
    normalized_name = normalize_item_name(item_name)
    has_stackable = any(normalize_item_name(i.get('name', '')) == normalized_name for i in items)
    return occupied_slots < 28 or has_stackable

def wait_for_next_tick(num_ticks: int = 1) -> None:
    current_tick = gametick().get('data', 0)
    target_tick = current_tick + num_ticks
    while gametick().get('data', 0) < target_tick:
        time.sleep(0.05)

def is_attacking():
    """Check if player is in attacking animation (11423)"""
    p_data = player(animation=True)
    if not p_data or 'data' not in p_data:
        return False
    return p_data['data'].get('animation', -1) == ATTACKING_ANIMATION

def has_banshee_dying_nearby():
    """Check if any Twisted Banshee nearby has death animation (1524)"""
    npc_data = npc(name='Twisted Banshee', size=15)
    if not npc_data or 'data' not in npc_data:
        return False
    for npc_info in npc_data['data']:
        if npc_info.get('animation') == BANSHEE_DEATH_ANIMATION:
            print("Banshee death detected nearby")
            return True
    return False

def has_loot_available():
    """Check if ANY lootable item exists nearby BEFORE attempting to loot"""
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return False
    loc = p_data['data'].get('location', {})
    player_x, player_y = loc.get('x'), loc.get('y')
    if player_x is None or player_y is None:
        return False
    
    for item_name in items_to_loot:
        ground_data = pick(player_x, player_y, size=12, item=item_name)
        if ground_data and 'data' in ground_data and ground_data['data'].get('items'):
            print(f"Loot found: {item_name}")
            return True
    return False

def pickup_closest_ground_item(item_name: str, tile_radius: int = 12) -> bool:
    normalized_search = normalize_item_name(item_name)
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        return False
    loc = p_data['data'].get('location', {})
    player_x, player_y = loc.get('x'), loc.get('y')
    if player_x is None or player_y is None:
        return False

    ground_data = pick(player_x, player_y, size=tile_radius, item=item_name)
    if not ground_data or 'data' not in ground_data or not ground_data['data'].get('items'):
        return False

    items = ground_data['data']['items']
    def dist(item_dict):
        tx = item_dict.get('tile', {}).get('x', 0)
        ty = item_dict.get('tile', {}).get('y', 0)
        return abs(tx - player_x) + abs(ty - player_y)
    items.sort(key=dist)
    target_item = items[0]

    if not can_pick_item(item_name):
        print(f"Inventory full, skipping {item_name}")
        return False

    print(f"Picking up {item_name}")

    mp = target_item['middle_point']
    screen_x, screen_y = runelite_window(mp['x'], mp['y'])
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.15, 0.35))

    hover_data = interact_options().get('data', [])
    can_left_click = False
    if hover_data:
        top = hover_data[0]
        option = top.get('option', '').lower()
        target_name = clean_target_name(top.get('target', ''))
        if option.startswith('take') and normalized_search in normalize_item_name(target_name):
            can_left_click = True

    if can_left_click:
        move(button='left', fast=True, sleep=True)
    else:
        move(button='right', fast=True, sleep=False)
        time.sleep(random.uniform(0.1, 0.25))
        menu_data = interact_options().get('data', [])
        take_entry = None
        for entry in menu_data:
            option = entry.get('option', '').lower()
            target_name = clean_target_name(entry.get('target', ''))
            if option.startswith('take') and normalized_search in normalize_item_name(target_name):
                take_entry = entry
                break
        if take_entry:
            menu_mp = take_entry['middle_point']
            mx, my = runelite_window(menu_mp['x'], menu_mp['y'])
            move(mx + random.randint(-12, 12), my + random.randint(-4, 4), fast=True, button='left', sleep=True)

    wait_for_next_tick(3)
    return True

def is_at_target_tile():
    player_data = player(location=True).get('data', {})
    loc = player_data.get('location', {})
    return (loc.get('x') == TARGET_TILE[0] and 
            loc.get('y') == TARGET_TILE[1] and 
            loc.get('plane', 0) == TARGET_TILE[2])

def move_to_target_tile():
    if not is_at_target_tile():
        print(f"Moving to safe spot {TARGET_TILE}")
        click_minimap_tile(TARGET_TILE[0], TARGET_TILE[1], 0, 0, target_zoom=2)
        while wait_for_tile_change(timeout_ticks=2):
            pass
        print("Arrived at safe spot")

def has_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False
    doses = ['(4)', '(3)', '(2)', '(1)']
    for item in inv_data['data']:
        name = item.get('name', '').strip()
        if any(name == f'Prayer potion{dose}' for dose in doses):
            return True
    return False

def drink_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        return False
    first_potion = None
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            first_potion = inv_item
            break
    if first_potion and 'middle_point' in first_potion:
        bounds = first_potion['middle_point']
        screen_x, screen_y = runelite_window(bounds['x'], bounds['y'])
        move(screen_x, screen_y, button='left', fast=True)
        print(f"Drank {first_potion.get('name', 'Prayer potion')}")
        wait_for_tick(1)
        return True
    return False

def check_prayer_level():
    player_data = player(prayer=True).get('data', {})
    return player_data.get('prayer', 0)

def is_inventory_full():
    inv_data = inventory().get('data', [])
    return len(inv_data) >= 28

def handle_login_screen(sleep=True):
    state = game_state().get('data')
    if state == "LOGIN_SCREEN":
        if sleep:
            sleep_time = random.uniform(35 * 60, 75 * 60)
            print(f"At login screen, sleeping {sleep_time / 60:.2f} minutes")
            time.sleep(sleep_time)
        rl_x, rl_y = runelite_window(0, 0)
        move(391 + rl_x, 303 + rl_y, button="left", fast=True)
        time.sleep(random.uniform(0.22, 0.3))
        move(391 + rl_x, 263 + rl_y, button="left", fast=True)
        time.sleep(1)
        print("Logged back in")
        return

def check_attack_status():
    """
    Check every tick for max 4 ticks if we're attacking (11423).
    If any tick shows 11423, return True (still in combat).
    """
    for _ in range(4):
        if is_attacking():
            print("Attack animation (11423) detected - still fighting")
            return True
        wait_for_next_tick(1)
    return False

def main():
    # Initial setup
    camera(pitch=400, yaw=200, zoom=300)
    click_run()
    combat_style('aggressive')  # Adjust for your weapon

    while True:
        handle_login_screen()
        
        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            break

        if not check_if_in_area(TWISTED_BANSHEE_AREA):
            print("Not in Twisted Banshee area – move there manually.")
            time.sleep(10)
            continue

        # Always return to safe spot first (prayer stays OFF)
        move_to_target_tile()

        # Drink prayer if low (prayer OFF on safe spot)
        if check_prayer_level() < 25:
            if has_prayer_potion():
                drink_prayer_potion()
            else:
                print("Out of prayer potions")

        # Check if we're still in combat (attacking animation)
        if check_attack_status():
            # Still fighting - check for banshee death
            if has_banshee_dying_nearby():
                print("Banshee dying - waiting for loot")
                wait_for_next_tick(4)  # Wait for death/loot
            continue  # Stay in combat loop

        # Not fighting - attack new target
        print("Not attacking - finding new Twisted Banshee")
        success = click_closest_npc([TWISTED_BANSHEE_ID], 'Attack')
        if not success:
            print("No Twisted Banshee found – waiting")
            time.sleep(2)
            continue

        # **ONLY check for loot if inventory not full**
        if not is_inventory_full():
            # **CRITICAL: Only check if loot actually exists BEFORE toggling prayer**
            if has_loot_available():
                print("Loot available - turning prayer ON for safe looting")
                toggle_prayer('PROTECT_FROM_MELEE', activate=True)
                
                # Now actually loot
                looted_something = False
                for item in items_to_loot:
                    while pickup_closest_ground_item(item, tile_radius=12):
                        looted_something = True
                        time.sleep(random.uniform(0.4, 0.8))
                
                # Return to safe spot and turn prayer OFF
                print("Looting complete - returning to safe spot, prayer OFF")
                move_to_target_tile()
                toggle_prayer('PROTECT_FROM_MELEE', activate=False)
            else:
                print("No loot available - skipping")
        else:
            print("Inventory full - skipping loot")

        time.sleep(0.6)  # Sync with game tick


def run():
    main()


if __name__ == "__main__":
    run()
