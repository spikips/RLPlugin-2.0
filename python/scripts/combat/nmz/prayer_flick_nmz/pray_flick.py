# pray_flick.py – UPDATED: ensures correct combat style every 100 flicks
from modules.core.plugin_client import player, gametick
from modules.widgets.widget import click_widget
from modules.core.ui_lock import ui_lock
from modules.utils.wait_for_tick import wait_for_tick 
from toggle_prayer import check_prayer
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style  # ← NEW
import asyncio

# Cached prayer state
prayer_points_cache = 0
prayer_active_cache = False

# NEW: Counter for combat-style check
flick_counter = 0


async def prayer_state_updater(poll_interval: float = 0.05):
    global prayer_points_cache, prayer_active_cache
    loop = asyncio.get_running_loop()
    while True:
        try:
            resp = await loop.run_in_executor(None, lambda: player(prayer=True))
            if resp and 'data' in resp and 'prayer' in resp['data']:
                prayer_points_cache = resp['data']['prayer']
            else:
                prayer_points_cache = 0
        except Exception:
            prayer_points_cache = 0

        try:
            prayer_active_cache = await loop.run_in_executor(None, lambda: check_prayer("PROTECT_FROM_MELEE"))
        except Exception:
            pass

        await asyncio.sleep(poll_interval)


def check_prayer_points():
    global prayer_points_cache
    if prayer_points_cache > 0:
        print(f"Prayer points: {prayer_points_cache} (Can flick: True)")
        return True
    else:
        print(f"Prayer points: {prayer_points_cache} (Can flick: False)")
        return False


async def wait_for_next_tick():
    loop = asyncio.get_running_loop()
    try:
        current_tick = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
    except Exception:
        current_tick = 0
    while True:
        await asyncio.sleep(0.01)
        try:
            new_tick = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
        except Exception:
            continue
        if new_tick != current_tick:
            return new_tick


async def flick_prayer_if_possible(start=False):
    if check_prayer_points():
        loop = asyncio.get_running_loop()
        try:
            is_active = await loop.run_in_executor(None, lambda: check_prayer("PROTECT_FROM_MELEE"))
        except Exception:
            is_active = prayer_active_cache

        clicks = 1 if start else (2 if is_active else 1)

        async with ui_lock:
            await loop.run_in_executor(None, lambda: click_widget('10485782', rand_x=3, rand_y=3, clicks=clicks, sleep_interval=(0.03, 0.05)))
        print(f"flick, clicks: {clicks}")
        return True
    else:
        print("Cannot flick: Prayer points are 0.")
        return False


async def flick_once():
    """Perform a single prayer flick iteration + combat-style check every 100 flicks."""
    global flick_counter

    await flick_prayer_if_possible()  

    # NEW: Every 100 flicks → ensure correct attack style (melee/range/magic)
    flick_counter += 1
    if flick_counter % 100 == 0:
        print(f"Ensuring correct combat style (flick #{flick_counter})...")
        try:
            loop = asyncio.get_running_loop()
            await loop.run_in_executor(None, ensure_correct_combat_style)
        except Exception as e:
            print(f"Combat style check failed (non-critical): {e}")


async def pray_flick():
    """Standalone infinite prayer flicking."""
    updater_task = asyncio.create_task(prayer_state_updater())
    await asyncio.sleep(0.05)
    await flick_prayer_if_possible(start=True)
    while True:
        await wait_for_next_tick()
        await flick_once()


def check_plane():
    data = player(location=True)
    if data and 'data' in data and 'location' in data['data']:
        plane = data['data']['location']['plane']
        print(f"Current plane: {plane}")
        if plane == 0:
            print("Exited NMZ (plane == 0).")
            exit()


if __name__ == "__main__":
    asyncio.run(pray_flick())