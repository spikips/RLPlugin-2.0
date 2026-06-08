import sys
import threading
import keyboard
import time
import random
from modules.core.mouse_control import move
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.core.plugin_client import get_active_prayers, interact_options
from modules.player_data.prayer.check_prayer_book import check_prayer_spellbook
from modules.widgets.widget_data import get_all_widget_data, get_widget_by_id 
from scripts.combat.moss_giant.ground_items import wait_for_next_tick 
from modules.utils.select_menu_option import select_menu_option
_prayer_lock = threading.Lock()

PRAYER_WIDGETS = {
    'PROTECT_FROM_MELEE': 35454999,
    'PROTECT_FROM_RANGE': 35454998,
    'PROTECT_FROM_MAGIC': 35454997,
    'STEEL_SKIN': 35454994,
    'PIETY': 35455011
}

def toggle_prayer(prayer_names, activate: bool = True, fast: bool = True):
    """Toggle prayers using targeted widget lookup + right-click menu (no more full widget dump)."""
    
    if not _prayer_lock.acquire(blocking=False):
        print(f"[Prayer Toggle] Skipped (already running)")
        return False

    try:
        if isinstance(prayer_names, str):
            prayer_names = [prayer_names]

        valid_prayers = [name for name in prayer_names if name in PRAYER_WIDGETS]
        if not valid_prayers:
            print("⚠️ No valid prayers specified")
            return False

        # Double-check current state *before* any book open or hover (user request #2).
        # This skips the entire prayer book interaction if we are already in the desired state.
        # Complements the check in ensure_protect_prayer / ensure_piety_on.
        try:
            prayer_data = get_active_prayers()
            if prayer_data and 'data' in prayer_data:
                active = prayer_data['data']
                all_match = True
                for name in valid_prayers:
                    currently_on = bool(active.get(name, False))
                    if currently_on != activate:
                        all_match = False
                        break
                if all_match:
                    print(f"[Prayer Toggle] Already {'on' if activate else 'off'}: {valid_prayers} — skipping book/hover entirely")
                    return True
        except Exception as e:
            print(f"[Prayer Toggle] Pre-check get_active_prayers failed (proceeding): {e}")

        print(f"[Prayer Toggle] {'Activating' if activate else 'Deactivating'} {valid_prayers} via menu")

        focus_runelite_window()

        # Safe prayer book open
        if not check_prayer_spellbook():
            for _ in range(3):
                keyboard.press_and_release("f2")
                wait_for_next_tick()
                if check_prayer_spellbook():
                    break
            wait_for_next_tick(2)

        success = True
        for name in valid_prayers:
            widget_id = PRAYER_WIDGETS[name]
            widget = get_widget_by_id(widget_id)
            
            if not widget or 'bounds' not in widget:
                print(f"⚠️ Widget bounds for {name} ({widget_id}) not found")
                success = False
                continue

            bounds = widget['bounds']
            print(f"[Prayer Toggle] Found bounds for {name}: {bounds}")
            cx = bounds['x'] + bounds['width'] // 2
            cy = bounds['y'] + bounds['height'] // 2

            option = "Activate" if activate else "Deactivate"

            # Probe the actual top menu option on the prayer icon by hovering.
            # This is the most reliable way to know if the prayer is currently on or off.
            # Fixes cases where get_active_prayers() desyncs and we try to "Activate"
            # something that is already active (only "Deactivate" is offered).
            try:
                rl_x, rl_y = runelite_window(0, 0)
                screen_x = rl_x + cx
                screen_y = rl_y + cy
                move(screen_x, screen_y, fast=fast, sleep=fast)
                time.sleep(random.uniform(0.03, 0.05))
                opts = interact_options().get('data', [])
                if opts:
                    first_opt = opts[0]['option'].lower()
                    is_currently_on = 'deactivate' in first_opt
                    if activate and is_currently_on:
                        print(f"[Prayer Toggle] {name} already active per in-game top option (Deactivate) — skipping")
                        continue
                    if not activate and not is_currently_on:
                        print(f"[Prayer Toggle] {name} already inactive per in-game top option (Activate) — skipping")
                        continue
            except Exception as e:
                print(f"[Prayer Toggle] In-game top-option probe failed for {name}, proceeding anyway: {e}")

            if select_menu_option(cx, cy, option, fast=fast):
                print(f"✅ {name} {option} successful")
            else:
                print(f"⚠️ Failed to select '{option}' for {name}")
                move(cx, cy - 50, fast=True)
                success = False

            wait_for_next_tick(2)  # small safety buffer

        # Hygiene move disabled for now per user request.
        # try:
        #     move(256, 180, fast=True)
        #     time.sleep(0.03)
        # except Exception:
        #     pass
        # (If we see the old menu/click problems return, we can un-comment and re-test.)

        return success

    finally:
        _prayer_lock.release()

# import time
# time.sleep(1)
# toggle_prayer("PROTECT_FROM_MELEE", activate=True, fast=True)