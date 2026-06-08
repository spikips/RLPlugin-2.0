# nmz_inside.py - FINAL: Lowest dose potions + Smart Quick Prayer
from modules.core.plugin_client import player, varbit, game_state, gametick, inventory, stats
from modules.utils.inventory import click_inventory, check_inventory
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.utils.drop_item import open_inventory_tab as open_inventory
from modules.core.window_utils import runelite_window
from modules.core.mouse_control import move
from potions import get_total_doses
from pray_flick import quick_prayer_double_click
from modules.utils.spec import spec
import asyncio
import json
import os
import random
from typing import Optional

# Load config for special attack threshold
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'config.json')
try:
    with open(json_path, 'r') as f:
        config = json.load(f)
        special_attack_threshold = config.get('special_attack_threshold')
except Exception:
    special_attack_threshold = None

# ====================== STATIC PRAYER MODE ======================
def check_prayer_level() -> int:
    data = player(prayer=True)
    return data['data'].get('prayer', 100) if data and 'data' in data else 100

def has_prayer_potion() -> bool:
    for item in inventory().get('data', []):
        if item.get('name', '').startswith('Prayer potion('):
            return True
    return False

async def drink_prayer_potion() -> bool:
    open_inventory()
    inv = inventory(middle_point=True)
    if not inv or 'data' not in inv:
        return False

    loop = asyncio.get_running_loop()
    for item in inv['data']:
        name = item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            mp = item.get('middle_point')
            if mp:
                sx, sy = runelite_window(mp['x'], mp['y'])
                await loop.run_in_executor(None, lambda: move(sx, sy, fast=False, sleep=False, button='left'))
                print(f"Drank {name}")
                await wait_for_next_tick(1)
                return True
    return False

async def manage_prayer(threshold: int) -> int | None:
    if check_prayer_level() <= threshold:
        if has_prayer_potion() and await drink_prayer_potion():
            new_threshold = random.randint(10, 25)
            print(f"Potion drunk - new prayer threshold {new_threshold}")
            return new_threshold
        print("Prayer low, no potion")
    return None

# ====================== COMMON HELPERS ======================
async def wait_for_next_tick(poll_interval: float = 0.05):
    loop = asyncio.get_running_loop()
    try:
        current = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
    except Exception:
        await asyncio.sleep(poll_interval)
        return
    while True:
        await asyncio.sleep(poll_interval)
        try:
            new = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
        except Exception:
            continue
        if new != current:
            return

# Drinks lowest dose first (exactly as you requested)
async def drink_potion(potion_base: str, max_retries: int = 2) -> bool:
    loop = asyncio.get_running_loop()
    for dose in range(1, 5):          # lowest dose first
        name = f"{potion_base} ({dose})"
        for _ in range(max_retries):
            success = await loop.run_in_executor(None, lambda n=name: click_inventory(n, action='Drink'))
            if success:
                await wait_for_next_tick()
                return True
            await wait_for_next_tick()
    return False

async def check_hp():
    try:
        return player(health=True).get('data', {}).get('health', 0)
    except Exception:
        return 0

# ====================== QUICK PRAYER CLICKER ======================
async def quick_prayer_clicker():
    while True:
        await asyncio.sleep(random.uniform(10, 50))
        await quick_prayer_double_click()

# ====================== FULL ABSORPTION MODE ======================
async def absorption_mode():
    print("=== FULL ABSORPTION MODE ===")
    print("-> Rock cake to 1 HP when HP < 50")
    print("-> Keep Absorption at 600 points")
    print("-> Overload only when HP >= 50")
    print("-> Quick Prayer clicked twice every 10-50 seconds")
    print("-> NO constant prayer flicking")

    max_hp = stats()['data'].get('Hitpoints', {}).get('level', 0)
    use_overload = max_hp >= 51
    print(f"Max HP: {max_hp} -> Overload {'ENABLED' if use_overload else 'DISABLED'}")

    quick_prayer_task = asyncio.create_task(quick_prayer_clicker())

    while True:
        await wait_for_next_tick()

        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            print("Left NMZ (plane changed). Stopping session.")
            quick_prayer_task.cancel()
            break

        current_hp = await check_hp()

        if current_hp > 1 and current_hp < 50:
            print(f"HP = {current_hp} (<50) -> rock caking to 1 HP")
            await rock_cake_to_one()

        if (varbit(3956) or 0) < 600:
            await drink_potion('Absorption')
            print(f"Absorption drunk -> current points: {varbit(3956) or 0}/600")

        if use_overload and (varbit(3955) or 0) == 0:
            if current_hp >= 50:
                print(f"HP = {current_hp} (>=50) -> drinking Overload")
                for _ in range(3):
                    if await drink_potion('Overload'):
                        await overload_and_rock(current_hp)
                        break
                else:
                    use_overload = False
            else:
                print(f"HP = {current_hp} (<50) -> skipping Overload")

async def rock_cake_to_one():
    loop = asyncio.get_running_loop()
    while True:
        hp = await check_hp()
        if hp <= 1:
            break
        num_clicks = random.randint(3, 5)
        for _ in range(num_clicks):
            hp = await check_hp()
            if hp <= 1:
                break
            await loop.run_in_executor(None, lambda: click_inventory('Dwarven rock cake', action='Guzzle'))
            await asyncio.sleep(0.02)
        await wait_for_next_tick()
    if await check_hp() == 1:
        print("HP = 1 - rock cake done")

async def overload_and_rock(start_hp: int):
    print(f"Drank overload at {start_hp} HP - waiting for 41+ damage...")
    while await check_hp() > start_hp - 41:
        await wait_for_next_tick()
    print(f"LOST {start_hp - await check_hp()} HP - SAFE!")
    await rock_cake_to_one()

# ====================== STATIC PRAYER MODE ======================
async def static_prayer_mode():
    print("=== STATIC PRAYER MODE (Prayer potions + Protect from Melee) ===")
    print("-> Protect from Melee turned on permanently")
    print("-> Prayer potion(4) drunk randomly between 10-25 prayer points")

    loop = asyncio.get_running_loop()
    await loop.run_in_executor(None, lambda: toggle_prayer("PROTECT_FROM_MELEE", activate=True))

    max_hp = stats()['data'].get('Hitpoints', {}).get('level', 0)
    use_overload = max_hp >= 51
    print(f"Max HP: {max_hp} -> Overload {'ENABLED' if use_overload else 'DISABLED'}")

    prayer_threshold = random.randint(10, 25)
    print(f"Initial prayer drink threshold: {prayer_threshold}")

    while True:
        await wait_for_next_tick()

        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            print("Left NMZ. Stopping session.")
            break

        if use_overload and (varbit(3955) or 0) == 0:
            if get_total_doses("overload") > 0:
                current_hp = await check_hp()
                if current_hp >= 51:
                    await drink_potion("Overload")
                else:
                    print(f"HP too low ({current_hp}) - skipping overload")
            else:
                use_overload = False

        new_threshold = await manage_prayer(prayer_threshold)
        if new_threshold is not None:
            prayer_threshold = new_threshold

        if random.random() < 0.3:
            await asyncio.sleep(0.1)

# ====================== MODE SELECTOR ======================
async def nmz_inside():
    print("=== NMZ INSIDE STARTED ===")

    if has_prayer_potion():
        await static_prayer_mode()
    else:
        await absorption_mode()

    print("nmz_inside session ended")

async def login_monitor():
    while True:
        try:
            if game_state().get('data') == "LOGIN_SCREEN":
                print("Logged out - stopping NMZ session.")
                return
        except Exception:
            pass
        await asyncio.sleep(1.0)

async def plane_monitor():
    while True:
        await asyncio.sleep(10)
        try:
            plane = player(location=True).get('data', {}).get('location', {}).get('plane', 0)
            if plane != 3:
                print(f"Left NMZ (plane {plane})")
                return
        except Exception:
            pass

async def nmz_inside_main():
    await asyncio.wait([
        asyncio.create_task(nmz_inside()),
        asyncio.create_task(login_monitor()),
        asyncio.create_task(plane_monitor())
    ], return_when=asyncio.FIRST_COMPLETED)

if __name__ == "__main__":
    asyncio.run(nmz_inside_main())