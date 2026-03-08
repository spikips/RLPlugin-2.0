# camera.py
from modules.core.plugin_client import player, game_state
from modules.core.mouse_control import move, get_cursor_pos, scroll
from modules.core.window_utils import runelite_window

import time
import random

ZOOM_LEVELS = [
    5668, 5283, 4924, 4589, 4277, 3986, 3715, 3463, 3227, 3008,
    2803, 2613, 2435, 2269, 2115, 1971, 1837, 1712, 1596, 1487,
    1386, 1292, 1204, 1122, 1046, 975, 908, 847, 789, 735,
    685, 639, 595, 555, 517, 482, 449, 419, 390, 364,
    339, 316, 294, 274, 256, 239, 222, 207, 193, 180,
    167, 155, 144, 134, 124, 116, 108, 101, 94, 87,
    81, 75, 70, 65, 61
]

def get_rl_bounds():
    try:
        x, y = runelite_window(0, 0)
        return x, y, 765, 503
    except:
        return 5, 121, 765, 503

def find_closest_index(zoom):
    return min(range(len(ZOOM_LEVELS)), key=lambda i: abs(ZOOM_LEVELS[i] - zoom))

def scroll_to_zoom(target_zoom, max_retries=15, speed=10):
    if not (61 <= target_zoom <= 5668):
        print("Invalid target zoom: " + str(target_zoom))
        return False

    for attempt in range(1, max_retries + 1):
        print("Zoom attempt " + str(attempt) + "/" + str(max_retries))
        current_zoom = player(camera=True).get('data', {}).get('camera', {}).get('zoom', 0)
        print("Current zoom: " + str(current_zoom))

        if abs(current_zoom - target_zoom) <= 55:
            print("Zoom within tolerance.")
            return True

        rl_x, rl_y, _, _ = get_rl_bounds()
        rx = rl_x + random.randint(180, 520)
        ry = rl_y + random.randint(120, 280)
        move(rx, ry, fast=True, sleep=True)

        curr_idx = find_closest_index(current_zoom)
        targ_idx = find_closest_index(target_zoom)
        steps = abs(targ_idx - curr_idx)
        scroll_dir = -1 if targ_idx > curr_idx else 1

        scroll_delay = 0.017 if speed >= 8 else 0.036

        for i in range(steps):
            scroll(scroll_dir, sleep=scroll_delay)
            if i % 5 == 4:
                time.sleep(0.035)

        time.sleep(0.13)

    final_zoom = player(camera=True).get('data', {}).get('camera', {}).get('zoom', 0)
    success = abs(final_zoom - target_zoom) <= 75
    print("Final zoom " + str(final_zoom) + " - " + ("success" if success else "failed"))
    return success

def drag_camera(dx, dy, speed=0.075):
    rl_x, rl_y, w, h = get_rl_bounds()

    safe_min_x = rl_x + 1
    safe_max_x = rl_x + 500
    safe_min_y = rl_y + 1
    safe_max_y = rl_y + 300

    start_x = (safe_min_x + safe_max_x) // 2
    start_y = (safe_min_y + safe_max_y) // 2

    if abs(dx) > 40 or abs(dy) > 40:
        if dx < 0: start_x = safe_max_x
        elif dx > 0: start_x = safe_min_x
        if dy < 0: start_y = safe_max_y
        elif dy > 0: start_y = safe_min_y

    start_x = max(safe_min_x, min(start_x, safe_max_x))
    start_y = max(safe_min_y, min(start_y, safe_max_y))

    move(start_x, start_y, fast=True, sleep=True)

    cx, cy = get_cursor_pos()
    target_x = max(1, min(1919, cx + dx))
    target_y = max(1, min(1079, cy + dy))

    move(button="middle", drag=True, x=target_x, y=target_y, fast=False, speed=speed)

    move((safe_min_x + safe_max_x) // 2, (safe_min_y + safe_max_y) // 2, fast=True, sleep=True)

def camera(pitch, yaw, zoom, speed=10):
    if not (0 <= pitch <= 2047 and 0 <= yaw <= 2047 and 61 <= zoom <= 5668):
        print("Invalid camera values")
        return False

    if game_state().get('data') != 'LOGGED_IN':
        print("Not logged in")
        return False

    scroll_to_zoom(380, speed=speed)

    print("=== Starting pitch/yaw adjustment ===")
    center_x = get_rl_bounds()[0] + 382
    center_y = get_rl_bounds()[1] + 251
    move(center_x, center_y, fast=True, sleep=True)

    MAX_ATTEMPTS = 12
    for attempt in range(1, MAX_ATTEMPTS + 1):
        cam = player(camera=True)['data']['camera']
        curr_p = cam['pitch']
        curr_y = cam['yaw']

        p_diff = pitch - curr_p
        y_diff = yaw - curr_y
        if y_diff > 1024: y_diff -= 2048
        elif y_diff < -1024: y_diff += 2048

        if abs(p_diff) <= 48 and abs(y_diff) <= 48:
            print("Camera reached target after " + str(attempt) + " attempts")
            break

        mult = 1.08 if attempt <= 3 else max(0.55, 0.92 - (attempt * 0.04))
        max_px = 490 if attempt <= 3 else max(42, 115 - attempt * 7)

        y_px = round(y_diff * 0.505 * mult)
        p_px = round(p_diff * 0.505 * mult)
        
        y_px = max(min(y_px, max_px), -max_px)
        p_px = max(min(p_px, max_px), -max_px)

        if 0 < abs(y_px) < 15: y_px = 15 * (1 if y_px > 0 else -1)
        if 0 < abs(p_px) < 15: p_px = 15 * (1 if p_px > 0 else -1)

        print("Attempt " + str(attempt) + ": dragging yaw_px=" + str(-y_px) + " pitch_px=" + str(p_px))
        drag_camera(-y_px, p_px, speed=0.068 + random.random()*0.028)

        time.sleep(0.07)

        if attempt == 6:
            print("Recovery drag...")
            drag_camera(-y_diff * 0.4, p_diff * 0.4, speed=0.11)

    final_success = scroll_to_zoom(zoom, speed=speed)
    
    print("Camera function completed.")
    return final_success