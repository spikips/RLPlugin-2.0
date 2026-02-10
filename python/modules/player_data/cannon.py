import time
from typing import Dict, Optional, Tuple
from modules.object_data.game_object import get_closest_game_object, get_game_objects
from modules.core.plugin_client import cannon_data, reset_cannon, get_varbits
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.object_data.object import get_closest_object
from modules.utils.select_menu_option import select_menu_option
from modules.utils.camera import camera
import time

def get_default_cannon_camera_settings() -> tuple[int, int]:
    return 512, 0

from modules.utils.camera import camera
import time
from modules.object_data.game_object import get_game_objects  # Ensure this is imported

def get_default_cannon_camera_settings() -> tuple[int, int]:
    return 512, 0

def click_cannon(
    action: str = 'Fire',
    exact_tile: Optional[Tuple[int, int, int]] = None,
    adjust_camera_if_offscreen: bool = True
) -> bool:
    CANVAS_X_MIN = 4
    CANVAS_X_MAX = 512
    CANVAS_Y_MIN = 4
    CANVAS_Y_MAX = 334

    is_repair = action.lower() == 'repair'
    cannon_ids = ['14916'] if is_repair else ['6', '7', '8', '9']
    print(f"Action is '{action}' - targeting cannon IDs {cannon_ids}")

    data = cannon_data().get('data', {})
    if not data.get('exists'):
        print("No cannon detected via cannon_data()")
        return False

    # Parse cannon tile
    pos_str = data.get('position', '')
    cannon_tile = None
    if 'WorldPoint' in pos_str:
        try:
            parts = pos_str.split('(')[1].split(')')[0].split(',')
            x = int(parts[0].split('=')[1].strip())
            y = int(parts[1].split('=')[1].strip())
            plane = int(parts[2].split('=')[1].strip())
            cannon_tile = (x, y, plane)
            print(f"Cannon detected at tile {cannon_tile}")
        except Exception as e:
            print(f"Failed to parse cannon position: {e}")
    else:
        print(f"Unexpected position format: {pos_str}")

    # Enforce exact_tile
    if exact_tile is not None:
        if cannon_tile != exact_tile:
            print(f"Cannon at {cannon_tile} != required tile {exact_tile} - skipping click")
            return False
        print(f"Cannon confirmed on required tile {exact_tile}")

    query_tile = exact_tile if exact_tile is not None else cannon_tile
    if query_tile is None:
        print("No valid tile for queries")
        return False

    def acquire_middle_point() -> Optional[Dict]:
        """Unified acquire: prefer cannon_data if valid/on-screen, else raw game_objects"""
        # Primary from cannon_data
        mp = data.get('middle_point')
        if mp:
            canvas_x = mp['x']
            canvas_y = mp['y']
            if CANVAS_X_MIN <= canvas_x <= CANVAS_X_MAX and CANVAS_Y_MIN <= canvas_y <= CANVAS_Y_MAX:
                print(f"Using primary cannon_data middle_point (on-screen): ({canvas_x}, {canvas_y})")
                return mp
            else:
                print(f"Primary middle_point ({canvas_x}, {canvas_y}) off-screen - falling to raw")

        # Raw fallback
        print("Acquiring middle_point via raw get_game_objects()")
        all_objs = get_game_objects()
        candidates = [
            o for o in all_objs
            if o.get('id') in [int(cid) for cid in cannon_ids] and
               (o.get('tile', {}).get('x'), o.get('tile', {}).get('y'), o.get('tile', {}).get('plane', 0)) == query_tile and
               'middle_point' in o
        ]
        if not candidates:
            print(f"Raw acquire failed - no candidates for IDs {cannon_ids} on tile {query_tile}")
            return None

        # Prefer on-screen
        on_screen = [c for c in candidates if CANVAS_X_MIN <= c['middle_point']['x'] <= CANVAS_X_MAX and CANVAS_Y_MIN <= c['middle_point']['y'] <= CANVAS_Y_MAX]
        best = on_screen[0] if on_screen else candidates[0]
        bx = best['middle_point']['x']
        by = best['middle_point']['y']
        status = "on-screen" if CANVAS_X_MIN <= bx <= CANVAS_X_MAX and CANVAS_Y_MIN <= by <= CANVAS_Y_MAX else "off-screen"
        print(f"Raw acquire SUCCESS: Selected middle_point ({bx}, {by}) ({status}) from {len(candidates)} candidates ({len(on_screen)} on-screen)")
        return best['middle_point']

    # Initial acquire
    mp = acquire_middle_point()
    if mp is None:
        print("Initial middle_point acquire failed")
        return False

    # Canvas check
    canvas_x = mp['x']
    canvas_y = mp['y']
    on_canvas = (CANVAS_X_MIN <= canvas_x <= CANVAS_X_MAX and
                 CANVAS_Y_MIN <= canvas_y <= CANVAS_Y_MAX)

    print(f"Current middle_point: ({canvas_x}, {canvas_y}) - {'ON-SCREEN' if on_canvas else 'OFF-SCREEN'}")

    if not on_canvas:
        if adjust_camera_if_offscreen:
            print("Adjusting camera to bring cannon on-screen...")
            pitch, yaw = get_default_cannon_camera_settings()
            if camera(pitch=pitch, yaw=yaw, zoom=200):
                print(f"Camera adjusted to pitch={pitch}, yaw={yaw}, zoom=200")
                time.sleep(1.5)

                # Post-camera re-acquire with retries
                mp = None
                for attempt in range(1, 11):
                    print(f"Post-camera acquire attempt {attempt}/10")
                    mp = acquire_middle_point()
                    if mp:
                        new_x = mp['x']
                        new_y = mp['y']
                        if CANVAS_X_MIN <= new_x <= CANVAS_X_MAX and CANVAS_Y_MIN <= new_y <= CANVAS_Y_MAX:
                            print(f"Post-camera SUCCESS: On-screen middle_point ({new_x}, {new_y})")
                            break
                    time.sleep(1.0)

                if mp is None or not (CANVAS_X_MIN <= mp['x'] <= CANVAS_X_MAX and CANVAS_Y_MIN <= mp['y'] <= CANVAS_Y_MAX):
                    print("Post-camera acquire failed - no on-screen middle_point after retries")
                    return False
            else:
                print("Camera adjustment failed")
                return False
        else:
            print("Off-screen and camera adjustment disabled")
            return False

    # Final click
    rl_x, rl_y = runelite_window(0, 0)
    abs_x = mp['x'] + rl_x
    abs_y = mp['y'] + rl_y
    print(f"CLICKING: Screen ({abs_x}, {abs_y}) | Canvas middle_point ({mp['x']}, {mp['y']}) | Action: '{action}'")

    success = select_menu_option(mp['x'], mp['y'], action)
    if success:
        print(f"Successfully performed '{action}' on cannon")
        return True
    else:
        print(f"Failed to perform '{action}' on cannon")
        return False
    

    
# Example: Reload cannon
# click_cannon('Pick-up', exact_tile=(3098, 9882, 0))

# Test cannon data
# print("Current cannon data:")
# reset_cannon()

# while True:
#    print(cannon_data())

# Optional reset
# print("Cannon data after reset:")
# print(cannon_data())