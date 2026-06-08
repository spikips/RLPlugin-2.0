# nmz_inside.py – FIXED: Flick-only mode now stays running forever on fresh accounts
from modules.core.plugin_client import player, varbit, game_state, gametick
from modules.utils.inventory import click_inventory, check_inventory
from pray_flick import pray_flick as external_pray_flick
from modules.utils.spec import spec
import asyncio
import gc
import json
import os
import random
from typing import Optional
from modules.core.plugin_client import stats
import sys
sys.stdout.reconfigure(encoding='utf-8', errors='replace')
sys.stderr.reconfigure(encoding='utf-8', errors='replace')
# Overload safety check at startup (base HP + current HP)
player_stats = stats()['data']
max_hp = player_stats.get('Hitpoints', {}).get('level', 0)
current_hp_at_start = player(health=True).get('data', {}).get('health', 0)
use_overload = max_hp >= 51
print(f"Max HP: {max_hp} | Current HP at start: {current_hp_at_start} → Overload {'ENABLED' if use_overload else 'DISABLED'}")

async def cancel_and_await(task: asyncio.Task, name: str = "task"):
    if task and not task.done():
        task.cancel()
        try:
            await asyncio.wait_for(task, timeout=1.0)
        except (asyncio.CancelledError, asyncio.TimeoutError):
            pass


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


# Config
script_dir = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(script_dir, 'config.json')
try:
    with open(json_path, 'r') as f:
        config = json.load(f)
        special_attack_threshold = config.get('special_attack_threshold')
except Exception:
    special_attack_threshold = None

has_potions = True


async def login_monitor():
    while True:
        try:
            if game_state().get('data') == "LOGIN_SCREEN":
                print("Logged out.")
                return
        except Exception:
            pass
        await asyncio.sleep(0.6)


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


async def check_hp():
    try:
        return player(health=True).get('data', {}).get('health', 0)
    except Exception:
        return 0


async def drink_potion(potion_base: str, max_retries: int = 2) -> bool:
    loop = asyncio.get_running_loop()
    for dose in range(1, 5):
        name = f"{potion_base} ({dose})"
        for _ in range(max_retries):
            success = await loop.run_in_executor(None, lambda n=name: click_inventory(n, action='Drink'))
            if success:
                await wait_for_next_tick()
                return True
            await wait_for_next_tick()
    return False


def has_absorption_potions() -> bool:
    return any(check_inventory(f"Absorption ({d})")[0] for d in range(1, 5))


async def rock_cake_to_one(current_flick_task: Optional[asyncio.Task] = None):
    if current_flick_task:
        await cancel_and_await(current_flick_task)
        print("Prayer flick paused during rock cake spam")

    loop = asyncio.get_running_loop()   # ← required for safe clicking

    while True:
        hp = await check_hp()
        if hp <= 1:
            break

        clicks = 0
        num_clicks = random.randint(3, 5)

        for _ in range(num_clicks):
            hp = await check_hp()
            if hp <= 1:
                break

            # Thread-safe click (prevents the RuntimeError you saw)
            clicked = await loop.run_in_executor(
                None,
                lambda: click_inventory('Dwarven rock cake', action='Guzzle')
            )

            if not clicked:
                break
            clicks += 1
            await asyncio.sleep(0.02)

        if clicks == 0:
            print("Rock cake failed this tick.")
            break

        await wait_for_next_tick()

    if await check_hp() == 1:
        print("HP = 1 – RESUMING PRAYER FLICK")

    await wait_for_next_tick()
    return asyncio.create_task(external_pray_flick())


async def overload_and_rock(start_hp: int, flick_task: Optional[asyncio.Task]):
    print(f"Drank overload at {start_hp} HP – waiting for 41+ damage...")
    while await check_hp() > start_hp - 41:
        await wait_for_next_tick()
    lost = start_hp - await check_hp()
    print(f"LOST {lost} HP – SAFE! SPAMMING ROCK CAKE")
    return await rock_cake_to_one(flick_task)


# NEW: Maintenance for FLICK-ONLY MODE (no rock cake spam)
async def flick_maintenance_no_rockcake(flick_task: asyncio.Task, spec_task: Optional[asyncio.Task]):
    global has_potions
    while True:
        await wait_for_next_tick()

        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            return 'exit'

        # Only potion checks (no rock cake)
        if has_potions and (varbit(3956) or 0) < 50:
            await drink_potion('Absorption')

        if has_potions and (varbit(3955) or 0) == 0:
            hp = await check_hp()
            if hp >= 51:
                for _ in range(3):
                    if await drink_potion('Overload'):
                        flick_task = await overload_and_rock(hp, flick_task)
                        break
                else:
                    has_potions = False

        if flick_task.done():
            return 'flick_done'


async def flick_maintenance(flick_task: asyncio.Task, spec_task: Optional[asyncio.Task]):
    global has_potions
    while True:
        await wait_for_next_tick()

        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            return 'exit'

        # Absorption (always)
        if has_potions and (varbit(3956) or 0) < 50:
            await drink_potion('Absorption')

        # Overload only if allowed AND current HP is safe
        if use_overload and has_potions and (varbit(3955) or 0) == 0:
            current_hp = await check_hp()
            if current_hp >= 51:
                for _ in range(3):
                    if await drink_potion('Overload'):
                        flick_task = await overload_and_rock(current_hp, flick_task)
                        break
                else:
                    has_potions = False
            else:
                print(f"Current HP ({current_hp}) < 51 → skipping overload")

        # Rock cake to 1 HP
        if await check_hp() > 1:
            flick_task = await rock_cake_to_one(flick_task)

        if flick_task.done():
            return 'flick_done'


async def nmz_absorption():
    absorption_points = varbit(3956) or 0
    has_abs = has_absorption_potions()
    flick_only = absorption_points == 0 and not has_abs

    if flick_only:
        print("=== FLICK-ONLY MODE (No absorption potions yet) ===")
        print("Just flicking prayer safely – rock cake spam disabled until you buy absorption.")
        flick_task = asyncio.create_task(external_pray_flick())
        spec_task = asyncio.create_task(spec_loop(special_attack_threshold)) if special_attack_threshold else None
        maintenance_task = asyncio.create_task(flick_maintenance_no_rockcake(flick_task, spec_task))
        await asyncio.wait([flick_task, maintenance_task], return_when=asyncio.FIRST_COMPLETED)
        return

    # Normal mode (has absorption)
    print("=== NORMAL MODE (Absorption available) ===")
    while True:
        await wait_for_next_tick()
        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            return

        flick_task = await handle_actions()
        if flick_task:
            spec_task = asyncio.create_task(spec_loop(special_attack_threshold)) if special_attack_threshold else None
            result = await asyncio.create_task(flick_maintenance(flick_task, spec_task))
            if result == 'exit':
                return


async def handle_actions() -> Optional[asyncio.Task]:
    global has_potions
    flick_task = None

    # Absorption (always)
    if has_potions and (varbit(3956) or 0) < 50:
        await drink_potion('Absorption')

    # Overload only if allowed AND current HP is safe
    if use_overload and has_potions and (varbit(3955) or 0) == 0:
        current_hp = await check_hp()
        if current_hp >= 51:
            print(f"Drank overload at {current_hp} HP – waiting for 41+ damage...")
            flick_task = asyncio.create_task(external_pray_flick())
            for _ in range(3):
                if await drink_potion('Overload'):
                    flick_task = await overload_and_rock(current_hp, flick_task)
                    if await check_hp() == 1:
                        return flick_task
                    break
            else:
                has_potions = False
                if flick_task:
                    await cancel_and_await(flick_task)
                return None
        else:
            print(f"Current HP ({current_hp}) < 51 → skipping overload")

    # Rock cake to 1 HP
    if await check_hp() > 1:
        flick_task = await rock_cake_to_one(flick_task)

    return flick_task if await check_hp() == 1 else None


async def spec_loop(threshold=None):
    while True:
        spec(threshold or 50)
        await wait_for_next_tick()


async def nmz_inside():
    print("=== NMZ INSIDE STARTED – PERFECT FOREVER WITH FRESH RESTARTS ===")

    await asyncio.wait([
        asyncio.create_task(nmz_absorption()),
        asyncio.create_task(login_monitor()),
        asyncio.create_task(plane_monitor())
    ], return_when=asyncio.FIRST_COMPLETED)

    print("nmz_inside finished – ready for fresh restart")


if __name__ == "__main__":
    asyncio.run(nmz_inside())