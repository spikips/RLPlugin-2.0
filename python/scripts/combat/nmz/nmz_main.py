# nmz_main.py – FINAL: Buys full set when possible, otherwise Prayer Fallback
import asyncio
import time
import gc
import sys
import random
import datetime
import json
import os

from check_area_start_and_open_bank import open_bank
from check_gear import check_gear
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
from nmz_bank import nmz_bank
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from nmz_dream import enter_dream
from check_nmz_chat_options import check_nmz_chat_options
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
from modules.object_data.game_object import click_gameobject, get_game_objects
from vial_ui import boss_config
from modules.widgets.widget import check_widget
from modules.utils.logout import logout_and_break
from scripts.combat.nmz.nmz_inside import nmz_inside
from modules.core.window_utils import focus_runelite_window
from modules.utils.logout import check_login_state_and_login
from buy_potions import main as buy_potions_main
from withdraw_potions import main as withdraw_potions_main
from modules.utils.inventory import check_inventory
from modules.utils.check_if_in_area import check_if_in_area
from modules.core.plugin_client import player, tile
from modules.weapon_data.combat_style import combat_style
from modules.player_data.check_run import click_run
from potions import get_total_doses

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'config.json')

with open(json_path, 'r') as f:
    config = json.load(f)

combat_style_mode = config.get('combat_style', None)
style = config.get('style', 'range')


def sleeptimer():
    sleep_minutes = random.randint(20, 80)
    current_time = datetime.datetime.now()
    end_time = current_time + datetime.timedelta(minutes=sleep_minutes)
    print(f"Current time: {current_time.strftime('%H:%M:%S')}")
    print(f"Sleep duration: {sleep_minutes} minutes")
    print(f"Timer will complete at: {end_time.strftime('%H:%M:%S')}")
    return sleep_minutes


def has_required_inventory(need_prayer_potions=False):
    # Pass prayer fallback flag to check_gear so it forces Monk's robes when needed
    gear_message, missing_items, _ = check_gear(prayer_fallback=need_prayer_potions)
    if missing_items:
        print("Gear check failed, proceeding to bank.")
        return False

    try:
        with open(json_path, 'r') as f:
            cfg = json.load(f)
            inventory_items_config = cfg.get('inventory_items', {}).get(style, [])
    except Exception:
        return False

    allowed_items = []
    for item_dict in inventory_items_config:
        name = item_dict.get('name', '').lower()
        if name.endswith('(4)'):
            base_name = name[:-3].strip()
            for dose in range(1, 5):
                allowed_items.append(f"{base_name} ({dose})")
        else:
            allowed_items.append(name)

    from modules.core.plugin_client import inventory
    inv_data = inventory().get('data', [])
    inventory_item_names = [item.get('name', '').lower().strip() for item in inv_data if 'name' in item]

    for item in inventory_item_names:
        if item not in allowed_items:
            print(f"Unexpected item in inventory: {item}, proceeding to bank.")
            return False

    rock_cake_present = check_inventory("dwarven rock cake")[0]
    if not rock_cake_present:
        print("Missing Dwarven rock cake, proceeding to bank.")
        return False

    print("Inventory contains required items and no unallowed items, skipping bank step.")
    return True


def main():
    print("=== Starting NMZ Setup Session ===")
    
    focus_runelite_window()
    time.sleep(0.5)
    check_login_state_and_login()

    data = player(location=True)
    if data and 'data' in data and 'location' in data['data']:
        plane = data['data']['location']['plane']
        if plane == 3:
            print("Already inside NMZ dream — skipping setup")
            return True

    # nmz_inside = check_if_in_area([
    #     "2600,3119,0", "2600,3083,0", "2629,3083,0", "2629,3119,0",
    #     "2611,3127,0", "2600,3120,0"
    # ], click=False)
    nmz_inside = check_if_in_area(["2592,3139,0", "2624,3139,0", "2642,3128,0", "2635,3109,0", "2630,3086,0", "2606,3087,0", "2586,3115,0", "2592,3138,0"
    ], click=False)

    if not nmz_inside:
        print("Not outside NMZ, aborting.")
        return False
    
    click_run()
    ensure_correct_combat_style()

    # Failsafe: If rewards chest not visible, move closer
    if not get_game_objects('26273'):
        print("Rewards chest not visible, moving closer...")
        click_minimap_tile(2608, 3114, 2, 2, target_zoom=2)
        while wait_for_tile_change(timeout_ticks=2):
            pass

    # === STORAGE CHECK + BUY + SMART FALLBACK ===
    print("Checking Rewards Chest (points + stored doses)...")
    buy_result = buy_potions_main(perform_buy=True)

    stored_abs = buy_result.get('stored_abs', 0)
    stored_ovl = buy_result.get('stored_ovl', 0)
    points = buy_result.get('points', 0)

    current_abs = get_total_doses("absorption")
    current_ovl = get_total_doses("overload")

    # TOTAL AVAILABLE = inventory + chest storage
    total_abs = current_abs + stored_abs
    total_ovl = current_ovl + stored_ovl

    needed_abs = max(0, 80 - total_abs)
    needed_ovl = max(0, 28 - total_ovl)
    total_cost = needed_abs * 1000 + needed_ovl * 1500

    print(f"Storage -> Abs: {stored_abs} | Ovl: {stored_ovl} | Points: {points}")
    print(f"Inventory -> Abs: {current_abs} | Ovl: {current_ovl}")
    print(f"Total available -> Abs: {total_abs} | Ovl: {total_ovl}")
    print(f"Still needed -> Abs: {needed_abs} | Ovl: {needed_ovl}")
    print(f"Total cost for full set: {total_cost} points")

    # === FINAL CLEAN FALLBACK LOGIC ===
    has_full_set = (total_abs >= 80 and total_ovl >= 28)
    can_afford_remaining = (points >= total_cost) and (needed_abs > 0 or needed_ovl > 0)

    if has_full_set or can_afford_remaining:
        need_prayer_potions = False
        if has_full_set:
            print("FULL POTION MODE → already have full set in storage/inventory")
        else:
            print("FULL POTION MODE → can afford to buy remaining potions")
    else:
        print("Not enough points + missing potions → Forcing PRAYER FALLBACK MODE")
        need_prayer_potions = True

    # Bank step (force it if prayer fallback)
    skipped_bank = has_required_inventory(need_prayer_potions=need_prayer_potions)
    if not skipped_bank or need_prayer_potions:
        if open_bank():
            nmz_bank(withdraw_prayer_potions=need_prayer_potions)
        else:
            print("Failed to open bank.")
            return False


    in_position = check_if_in_area(["2600,3119,0", "2600,3112,0", "2612,3112,0", "2612,3124,0", "2604,3120,0", "2601,3119,0"], click=False)
    # in_position = check_if_in_area(["2592,3139,0", "2624,3139,0", "2642,3128,0", "2635,3109,0", "2630,3086,0", "2606,3087,0", "2586,3115,0", "2592,3138,0"], click=False)
    if not in_position:
        click_minimap_tile(2608, 3114, 2, 2, target_zoom=2)
        while wait_for_tile_change(timeout_ticks=2):
            pass

    camera(pitch=456, yaw=174, zoom=356)
    if combat_style_mode is not None:
        combat_style(combat_style_mode)

    if not enter_dream() or not check_nmz_chat_options():
        return False

    wait_for_tick(1)

    # === BARREL WITHDRAW ONLY IF WE ARE IN FULL POTION MODE ===
    if need_prayer_potions:
        print("Prayer Fallback Mode - skipping barrel withdrawal (using Prayer potions + rock cake)")
    else:
        print("Withdrawing potions from barrels...")
        withdraw_potions_main(stored_abs=stored_abs, stored_ovl=stored_ovl)

    click_gameobject('26291', 'Drink', (2605, 3117), 5)

    for _ in range(20):
        if check_widget('8454146'):
            boss_config()
            break
        wait_for_tick(1)
    else:
        print("Vial UI never appeared.")
        return False

    print("Successfully entered NMZ dream.")
    wait_for_tick(2)

    current_tile = tile(tile_radius=0)
    if current_tile and 'data' in current_tile and current_tile['data']:
        tile_data = current_tile['data'][0]
        x = tile_data['x'] - 8
        y = tile_data['y'] + 18
        click_minimap_tile(x, y, 0, 0, target_zoom=2)
        while wait_for_tile_change(timeout_ticks=2):
            pass
        print("Character in safe spot — SETUP COMPLETE!")

    return True


if __name__ == "__main__":
    cycle = 1
    while True:
        print(f"\n=== NMZ CYCLE #{cycle} – FRESH START (ZERO LAG) ===")
        
        if not main():
            print("Setup failed — retrying in 10s...")
            time.sleep(10)
            continue

        print("Setup complete — starting FRESH nmz_inside")

        try:
            asyncio.run(nmz_inside())
        except Exception as e:
            print(f"nmz_inside crashed: {e}")

        focus_runelite_window()
        print("Session ended — taking break...")
        logout_and_break(sleeptimer())

        gc.collect()
        time.sleep(3)

        cycle += 1
        print(f"=== CYCLE #{cycle} READY – FRESH AS NEW ===")