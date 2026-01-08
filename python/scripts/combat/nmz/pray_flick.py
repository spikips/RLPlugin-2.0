from modules.core.plugin_client import player, gametick
from modules.widgets.widget import click_widget
from modules.core.ui_lock import ui_lock
from modules.utils.wait_for_tick import wait_for_tick 
from toggle_prayer import check_prayer
import asyncio

# Cached prayer state populated by background updater to keep hot-path fast
prayer_points_cache = 0
prayer_active_cache = False


async def prayer_state_updater(poll_interval: float = 0.05):
    """Background task that refreshes prayer points and active state.

    Polls the plugin at a short interval and updates module-level caches so
    the per-tick flick path can read cached values without blocking RPCs.
    """
    global prayer_points_cache, prayer_active_cache
    loop = asyncio.get_running_loop()
    while True:
        try:
            # Offload blocking player() RPC to thread executor
            resp = await loop.run_in_executor(None, lambda: player(prayer=True))
            if resp and 'data' in resp and 'prayer' in resp['data']:
                prayer_points_cache = resp['data']['prayer']
            else:
                prayer_points_cache = 0
        except Exception:
            prayer_points_cache = 0

        try:
            # check_prayer may perform blocking calls; run it in executor as well
            prayer_active_cache = await loop.run_in_executor(None, lambda: check_prayer("PROTECT_FROM_MELEE"))
        except Exception:
            # Keep previous value if check fails
            pass

        await asyncio.sleep(poll_interval)

def check_prayer_points():
    """
    Check if prayer points are greater than 0.
    
    Returns:
        bool: True if prayer points > 0 (can flick), False if == 0.
    """
    # Use cached value populated by the background updater to avoid RPCs
    global prayer_points_cache
    if prayer_points_cache > 0:
        print(f"Prayer points: {prayer_points_cache} (Can flick: True)")
        return True
    else:
        print(f"Prayer points: {prayer_points_cache} (Can flick: False)")
        return False

async def wait_for_next_tick():
    loop = asyncio.get_running_loop()
    # Offload gametick() RPCs to executor so we don't block the event loop
    try:
        current_tick = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
    except Exception:
        current_tick = 0
    while True:
        await asyncio.sleep(0.01)  # Reduced poll interval for better timing
        try:
            new_tick = await loop.run_in_executor(None, lambda: gametick().get('data', 0))
        except Exception:
            continue
        if new_tick != current_tick:
            # print('tick changed', new_tick)
            return new_tick

async def flick_prayer_if_possible(start=False):
    """
    Check if prayer points > 0 and, if true, click the prayer widget to flick.
    
    Returns:
        bool: True if flicked, False otherwise.
    """
    if check_prayer_points():
        # Determine current prayer active state right before clicking.
        # Run the potentially blocking `check_prayer` in the executor so we
        # sample a fresh value but don't block the event loop.
        loop = asyncio.get_running_loop()
        try:
            is_active = await loop.run_in_executor(None, lambda: check_prayer("PROTECT_FROM_MELEE"))
        except Exception:
            # Fall back to cached state if executor call fails
            is_active = prayer_active_cache

        # If start=True, prefer a single click to ensure the prayer is turned on
        if start:
            clicks = 1
        else:
            # If prayer is currently active, use 2 clicks (flick); if inactive, only 1 click
            clicks = 2 if is_active else 1

        # Perform the clicks under a global UI lock to prevent concurrent UI actions
        # from other tasks interfering with timing/state.
        async with ui_lock:
            loop = asyncio.get_running_loop()
            # Run blocking click_widget in executor to avoid blocking the event loop
            await loop.run_in_executor(None, lambda: click_widget('10485782', rand_x=3, rand_y=3, clicks=clicks, sleep_interval=(0.03, 0.05)))  # Slightly reduced sleep for tighter timing
        print(f"flick, clicks: {clicks}")
        return True
    else:
        print("Cannot flick: Prayer points are 0.")
        return False

async def flick_once():
    """Perform a single prayer flick iteration (non-blocking)."""
    await flick_prayer_if_possible()  # Removed the extra wait_for_next_tick here to avoid skipping ticks

async def pray_flick():
    """Standalone infinite prayer flicking (for testing/direct run)."""
    # Start the background updater and give it a moment to populate caches
    updater_task = asyncio.create_task(prayer_state_updater())
    await asyncio.sleep(0.05)
    await flick_prayer_if_possible(start=True)  # Initial turn on and wait for next tick
    while True:
        await wait_for_next_tick()
        await flick_once()
        # Do not attempt an immediate corrective click in the same tick; allow
        # the next tick's flick to re-evaluate and act. Immediate re-clicking
        # can cause multiple clicks in the same tick and lead to looping.

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

    # check_plane()

# 3956 abs
# 3955 overload