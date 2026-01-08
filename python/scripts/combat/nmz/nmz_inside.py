# nmz_inside.py – FINAL: EXACT ORIGINAL BEHAVIOR + ZERO EXHAUSTION + FRESH RESTART COMPATIBLE
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
    for dose in range(1, 5):
        name = f"{potion_base} ({dose})"
        for _ in range(max_retries):
            if click_inventory(name, action='Drink'):
                await wait_for_next_tick()
                return True
            await wait_for_next_tick()
    return False


def has_absorption_potions() -> bool:
    return any(check_inventory(f"Absorption ({d})")[0] for d in range(1, 5))


# ORIGINAL AGGRESSIVE ROCK CAKE SPAM
async def rock_cake_to_one(current_flick_task: Optional[asyncio.Task] = None):
    if current_flick_task:
        await cancel_and_await(current_flick_task)
        print("Prayer flick paused during rock cake spam")

    loop = asyncio.get_running_loop()
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
            clicked = await loop.run_in_executor(None, lambda: click_inventory('Dwarven rock cake', action='Guzzle'))
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


# 41+ DAMAGE → PAUSE FLICK + SPAM CAKE + RESUME AT 1 HP
async def overload_and_rock(start_hp: int, flick_task: Optional[asyncio.Task]):
    print(f"Drank overload at {start_hp} HP – waiting for 41+ damage...")
    while await check_hp() > start_hp - 41:
        await wait_for_next_tick()
    lost = start_hp - await check_hp()
    print(f"LOST {lost} HP – SAFE! SPAMMING ROCK CAKE")
    return await rock_cake_to_one(flick_task)


async def handle_actions() -> Optional[asyncio.Task]:
    global has_potions
    flick_task = None

    if has_potions and (varbit(3956) or 0) < 50:
        await drink_potion('Absorption')

    if has_potions and (varbit(3955) or 0) == 0:
        hp = await check_hp()
        if hp >= 51:
            flick_task = asyncio.create_task(external_pray_flick())
            for _ in range(3):
                if await drink_potion('Overload'):
                    flick_task = await overload_and_rock(hp, flick_task)
                    if await check_hp() == 1:
                        return flick_task
                    break
            else:
                has_potions = False
                if flick_task:
                    await cancel_and_await(flick_task)
                return None

    if await check_hp() > 1:
        flick_task = await rock_cake_to_one(flick_task)

    return flick_task if await check_hp() == 1 else None


async def spec_loop(threshold=None):
    while True:
        spec(threshold or 50)
        await wait_for_next_tick()


async def flick_maintenance(flick_task: asyncio.Task, spec_task: Optional[asyncio.Task]):
    global has_potions
    while True:
        await wait_for_next_tick()

        if player(location=True).get('data', {}).get('location', {}).get('plane', 0) != 3:
            return 'exit'

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

        if await check_hp() > 1:
            flick_task = await rock_cake_to_one(flick_task)

        if flick_task.done():
            return 'flick_done'


async def nmz_absorption():
    flick_only = (varbit(3956) or 0) == 0 and not has_absorption_potions()

    if flick_only:
        print("=== FLICK-ONLY MODE ===")
        flick_task = asyncio.create_task(external_pray_flick())
        spec_task = asyncio.create_task(spec_loop(special_attack_threshold)) if special_attack_threshold else None
        await asyncio.wait([flick_task, asyncio.create_task(flick_maintenance(flick_task, spec_task))], return_when=asyncio.FIRST_COMPLETED)
        return

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