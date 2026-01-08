# humanlike_interact.py
import random
import time
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.widgets.widget_data import get_all_widget_data
from modules.utils.wait_for_tick import wait_for_tick

# List of widget IDs that represent interface tabs / spellbook / prayer book / etc.
HUMANLIKE_WIDGET_IDS = [
    35913792,  # Combat tab
    35913793,  # Stats tab
    35913794,  # Quest tab
    35913796,  # Prayer tab (spellbook)
    35913797,  # Magic tab
    35913798,  # Inventory tab
    35913785,  # Equipment tab
]

# The inventory tab we want to click after selecting another tab
INVENTORY_WIDGET_ID = 35913802

# Screen area for right-click (safe top-left area)
RIGHT_CLICK_MIN_X = 15
RIGHT_CLICK_MIN_Y = 15
RIGHT_CLICK_MAX_X = 500
RIGHT_CLICK_MAX_Y = 320


def get_widget_bounds(widget_id: int) -> tuple[int, int, int, int] | None:
    widgets = get_all_widget_data()
    if not widgets:
        return None

    for widget in widgets:
        if widget.get("id") == widget_id and 'bounds' in widget:
            bounds = widget['bounds']
            return (
                bounds['x'],
                bounds['y'],
                bounds['width'],
                bounds['height']
            )
    return None


def random_tab_click() -> bool:
    if random.random() > 0.2:
        return False

    print("[HUMANLIKE] Performing random tab click...")

    target_id = random.choice(HUMANLIKE_WIDGET_IDS)
    bounds = get_widget_bounds(target_id)
    if not bounds:
        print(f"[HUMANLIKE] Widget {target_id} not found.")
        return False

    x, y, w, h = bounds
    click_x = x + random.randint(5, max(5, w - 5))
    click_y = y + random.randint(5, max(5, h - 5))

    screen_x, screen_y = runelite_window(click_x, click_y)
    print(f"[HUMANLIKE] Clicking tab {target_id} at ({click_x}, {click_y})")
    move(screen_x, screen_y, button='left', fast=False, sleep=True)

    # === CHANGED: Weighted random wait time (favors short durations) ===
    # Triangular distribution: peak at ~1–5s, tail to 30s
    # We use random.triangular(low, mode, high)
    # - low = 1s
    # - mode = 3s (peak probability)
    # - high = 30s (very rare)
    time_to_sleep = random.triangular(1, 3, 30)  # mode at 3 seconds

    print(f"[HUMANLIKE] Waiting {time_to_sleep:.2f}s before returning to inventory...")
    time.sleep(time_to_sleep)

    inv_bounds = get_widget_bounds(INVENTORY_WIDGET_ID)
    if not inv_bounds:
        print("[HUMANLIKE] Inventory tab (35913802) not found.")
        return True

    inv_x, inv_y, inv_w, inv_h = inv_bounds
    inv_click_x = inv_x + random.randint(5, max(5, inv_w - 5))
    inv_click_y = inv_y + random.randint(5, max(5, inv_h - 5))

    inv_screen_x, inv_screen_y = runelite_window(inv_click_x, inv_click_y)
    print(f"[HUMANLIKE] Returning to inventory at ({inv_click_x}, {inv_click_y})")
    move(inv_screen_x, inv_screen_y, button='left', fast=False, sleep=True)

    return True


def random_right_click_area() -> bool:
    if random.random() > 0.80:
        return False

    print("[HUMANLIKE] Performing random right-click in screen area...")

    click_x = random.randint(RIGHT_CLICK_MIN_X, RIGHT_CLICK_MAX_X)
    click_y = random.randint(RIGHT_CLICK_MIN_Y, RIGHT_CLICK_MAX_Y)

    screen_x, screen_y = runelite_window(click_x, click_y)
    print(f"[HUMANLIKE] Right-click at screen ({screen_x}, {screen_y})")
    move(screen_x, screen_y, button='right', fast=False, sleep=True)

    time.sleep(random.uniform(0.4, 1.2))

    # Simulate natural mouse movement after right-click
    direction = random.choice([-1, 1])
    x_offset = direction * random.randint(70, 150)
    y_offset = -random.randint(5, 40)

    new_x = screen_x + x_offset
    new_y = screen_y + y_offset

    # Clamp to rough screen bounds
    new_x = max(100, min(new_x, 1200))
    new_y = max(100, min(new_y, 800))

    print(f"[HUMANLIKE] Moving mouse to ({new_x}, {new_y}) after right-click")
    move(new_x, new_y, button=None, fast=False, sleep=True)

    return True


def perform_humanlike_interaction() -> None:
    print("[HUMANLIKE] Deciding interaction...")

    if random_tab_click():
        print("[HUMANLIKE] Tab interaction completed.")
        return

    if random_right_click_area():
        print("[HUMANLIKE] Random right-click + mouse movement completed.")
        return

    print("[HUMANLIKE] No interaction this time.")


if __name__ == "__main__":
    perform_humanlike_interaction()