from modules.core.plugin_client import player, game_state
from modules.core.mouse_control import move, get_cursor_pos, scroll
from modules.core.window_utils import runelite_window

import time
import random


# spellbook Id	35913797, SpriteId	-1 when disabled 
# varrock teleport Id	14286871, spriteid 27 when enough runes 
# Bounds	java.awt.Rectangle[x=590,y=268,width=24,height=24]

# Zoom levels for scroll adjustments
# ZOOM_LEVELS = [1940, 1579, 1285, 1046, 851, 693, 564, 459, 373, 304, 247, 201, 163, 132, 107, 87, 71, 61]
ZOOM_LEVELS = [1448, 1349, 1257, 1172, 1092, 1018, 949, 884, 824, 768, 716, 667, 622, 579, 540, 503, 469, 437, 407, 380, 354, 330, 307, 286, 266, 248, 231, 215, 200, 186, 181]

def scroll_to_zoom(target_zoom: int, max_retries: int = 30, speed: int = 10) -> bool:
    """
    Adjust the camera zoom to the target zoom level using scroll.
    Moves mouse to a random point within client bounds before scrolling.
    Uses ZOOM_LEVELS to determine how many scrolls are needed.
    Retries up to max_retries times if the final zoom is not within tolerance.
    
    Args:
        target_zoom (int): Desired zoom level.
        max_retries (int): Maximum number of retry attempts (default: 10).
        speed (int): Scroll speed, from 1 (slowest, 0.1s delay) to 10 (fastest, 0.015-0.04s random delay) (default: 1).
    
    Returns:
        bool: True if zoom adjusted successfully, False otherwise.
    """
    if target_zoom < 61 or target_zoom > 1940:
        print(f"Invalid target zoom: {target_zoom}. Must be between 61 and 1940.")
        return False
    if not (1 <= speed <= 10):
        print(f"Invalid speed: {speed}. Must be between 1 and 10.")
        return False

    for attempt in range(1, max_retries + 1):
        print(f"Zoom adjustment attempt {attempt}/{max_retries}")

        # Get client bounds
        rl_x, rl_y = runelite_window(0, 0)
        width, height = 480, 300
        min_x, max_x = rl_x + 10, rl_x + width
        min_y, max_y = rl_y + 10, rl_y + height

        camera_data = player(camera=True).get('data', {}).get('camera', {})
        current_zoom = camera_data.get('zoom', 0)
        print(f"Current zoom: {current_zoom}")

        if abs(current_zoom - target_zoom) <= 50:
            print("Zoom already within tolerance of target level.")
            return True

        # Move mouse to random point within client bounds
        random_x = random.randint(min_x, max_x)
        random_y = random.randint(min_y, max_y)
        if attempt <= 1:
            move(random_x, random_y, fast=True)
            print(f"Moved mouse to random point ({random_x}, {random_y}) within client bounds")
            time.sleep(0.05)  # Small delay for stability

        # Find the closest zoom level in ZOOM_LEVELS
        def find_closest_zoom(zoom):
            return min(ZOOM_LEVELS, key=lambda x: abs(x - zoom))

        # Determine scroll direction and count
        scrolls_needed = 0
        current_level = find_closest_zoom(current_zoom)
        current_index = ZOOM_LEVELS.index(current_level)

        # Calculate sleep based on speed (linear interpolation between 0.1s at speed 1 and 0.015-0.04s at speed 10)
        if speed == 1:
            scroll_delay = 0.1
        elif speed == 10:
            scroll_delay = random.uniform(0.015, 0.04)
        else:
            # Linearly interpolate between 0.1s (speed 1) and 0.0275s (average of 0.015-0.04s for speed 10)
            max_delay = 0.0275  # Average of 0.015 and 0.04
            delay = 0.1 - ((speed - 1) / 9) * (0.1 - max_delay)
            scroll_delay = random.uniform(max(0.015, delay - 0.0125), min(0.04, delay + 0.0125))

        if current_zoom < target_zoom:
            # Need to zoom in (scroll up)
            while current_level < target_zoom and current_index > 0:
                current_index -= 1
                current_level = ZOOM_LEVELS[current_index]
                scrolls_needed += 1
                scroll(1, sleep=scroll_delay)
        else:
            # Need to zoom out (scroll down)
            while current_level > target_zoom and current_index < len(ZOOM_LEVELS) - 1:
                current_index += 1
                current_level = ZOOM_LEVELS[current_index]
                scrolls_needed += 1
                scroll(-1, sleep=scroll_delay)

        # Small delay before verifying final zoom
        time.sleep(0.1)

        # Verify final zoom
        camera_data = player(camera=True).get('data', {}).get('camera', {})
        final_zoom = camera_data.get('zoom', 0)
        print(f"Final zoom: {final_zoom}, Scrolls performed: {scrolls_needed}")

        if abs(final_zoom - target_zoom) <= 50:
            print("Zoom adjusted successfully.")
            return True

    print(f"Failed to adjust zoom to {target_zoom} after {max_retries} attempts.")
    return False

def camera(pitch: int, yaw: int, zoom: int, speed=10) -> bool:
    """
    Adjust the RuneScape camera to the specified pitch, yaw, and zoom.
    Ensures zoom is at least 300 before movement, then sets final zoom.
    Uses a 1:2 pixel-to-unit ratio for pitch/yaw adjustments.
    
    Args:
        pitch (int): Target pitch (0 to 2047).
        yaw (int): Target yaw (0 to 2047).
        zoom (int): Target zoom (61 to 1940).
    
    Returns:
        bool: True if adjusted successfully, False otherwise.
    """
    
    # Validate input
    if not (0 <= pitch <= 2047):
        print(f"Invalid pitch: {pitch}. Must be between 0 and 2047.")
        return False
    if not (0 <= yaw <= 2047):
        print(f"Invalid yaw: {yaw}. Must be between 0 and 2047.")
        return False
    if not (61 <= zoom <= 1940):
        print(f"Invalid zoom: {zoom}. Must be between 61 and 1940.")
        return False

    # Check game state
    state_response = game_state()
    if not state_response or state_response.get('data') != 'LOGGED_IN':
        print(f"Cannot adjust camera: Game state is {state_response}, expected {'data': 'LOGGED_IN'}")
        return False

    # Ensure zoom is at least 300 before moving camera
    camera_data = player(camera=True).get('data', {}).get('camera', {})
    current_zoom = camera_data.get('zoom', 0) 
    current_pitch = camera_data.get('pitch', 0)
    current_yaw = camera_data.get('yaw', 0)

    if abs(pitch - current_pitch) <= 50 and abs(yaw - current_yaw) <= 50:
        print("Camera pitch and yaw already within tolerance (±50). No adjustment needed.")
        # Still adjust zoom if needed
        if not scroll_to_zoom(zoom, speed=speed):
            print("Failed to adjust zoom.")
            return False
        return True
    
    if current_zoom < 300:
        print(f"Current zoom {current_zoom} is less than 300. Adjusting to 300.")
        if not scroll_to_zoom(300, speed=speed):
            print("Failed to adjust zoom to 300.")
            return False

    # Client window bounds
    rl_x, rl_y = runelite_window(0, 0)
    width, height = 515, 337
    min_x, max_x = rl_x, rl_x + width
    min_y, max_y = rl_y, rl_y + height
    center_x = (min_x + max_x) // 2
    center_y = (min_y + max_y) // 2
    print(f"Client bounds: width={width}, height={height}, rl_x={rl_x}, rl_y={rl_y}")

    initial_camera_data = player(camera=True).get('data', {}).get('camera', {})
    initial_pitch = initial_camera_data['pitch']
    initial_yaw = initial_camera_data['yaw']
    print(f"Initial - Pitch: {initial_pitch}, Yaw: {initial_yaw}")

    # Perform up to two adjustment passes
    for pass_num in range(1, 20):
        print(f"\n--- Starting Pass {pass_num} ---")
        camera_data = player(camera=True).get('data', {}).get('camera', {})
        current_pitch = camera_data['pitch']
        current_yaw = camera_data['yaw']
        print(f"Pass {pass_num} - Current Pitch: {current_pitch}, Yaw: {current_yaw}")

        # Check if within tolerance
        if abs(current_pitch - pitch) <= 20 and abs((current_yaw - yaw) % 2048) <= 20:
            print(f"Camera adjusted successfully after Pass {pass_num}")
            # Set final zoom
            if not scroll_to_zoom(zoom, speed=speed):
                print("Failed to set final zoom.")
                return False
            return True

        # Calculate differences
        pitch_diff = pitch - current_pitch  # Pitch is linear, no shortest path
        yaw_diff = yaw - current_yaw
        # Shortest path for yaw (circular)
        if yaw_diff > 1024:
            yaw_diff -= 2048
        elif yaw_diff < -1024:
            yaw_diff += 2048

        # Total mouse movement (1:2 ratio)
        x_move = -yaw_diff // 2  # 1 pixel for every 2 yaw units
        y_move = pitch_diff // 2  # 1 pixel for every 2 pitch units
        print(f"Pass {pass_num} - Need to move - X: {x_move}, Y: {y_move}")

        remaining_x = x_move
        remaining_y = y_move
        segment_count = 0

        # Break into manageable drags
        while abs(remaining_x) > 0 or abs(remaining_y) > 0:
            start_x = center_x
            start_y = center_y

            # Calculate movement for this segment
            this_x = remaining_x
            this_y = remaining_y

            # Clamp to client bounds
            target_x = start_x + this_x
            target_y = start_y + this_y
            if target_x < min_x:
                this_x = min_x - start_x
            elif target_x > max_x:
                this_x = max_x - start_x
            if target_y < min_y:
                this_y = min_y - start_y
            elif target_y > max_y:
                this_y = max_y - start_y

            target_x = start_x + this_x
            target_y = start_y + this_y

            # Perform the drag
            move(start_x, start_y, fast=True)
            print(f"Pass {pass_num} - Moved mouse to ({start_x}, {start_y})")
            time.sleep(0.03)
            move(button="middle", drag=True, x=target_x, y=target_y, fast=False, speed=0.1)
            print(f"Pass {pass_num} - Dragged from ({start_x}, {start_y}) to ({target_x}, {target_y})")
            current_pos = get_cursor_pos()
            print(f"Pass {pass_num} - Actual mouse position after drag: ({current_pos[0]}, {current_pos[1]})")

            # Update remaining movement
            remaining_x -= this_x
            remaining_y -= this_y
            segment_count += 1
        print(f"Pass {pass_num} - Completed {segment_count} drag segments")

    # Final camera state
    camera_data = player(camera=True).get('data', {}).get('camera', {})
    current_pitch = camera_data['pitch']
    current_yaw = camera_data['yaw']
    print(f"\nFinal - Pitch: {current_pitch}, Yaw: {current_yaw}")

    # Calculate and print differences and ratios
    pitch_change = current_pitch - initial_pitch
    yaw_change = current_yaw - initial_yaw
    print(f"Pitch change (final - initial): {pitch_change}")
    print(f"Yaw change (final - initial): {yaw_change}")

    # Calculate ratios, handling division by zero
    pitch_ratio = y_move / pitch_change if pitch_change != 0 else "undefined (pitch_change is 0)"
    yaw_ratio = x_move / yaw_change if yaw_change != 0 else "undefined (yaw_change is 0)"
    print(f"y_move / Pitch change: {pitch_ratio}")
    print(f"x_move / Yaw change: {yaw_ratio}")

    # Set final zoom even if camera adjustment fails
    if not scroll_to_zoom(zoom, speed=speed):
        print("Failed to set final zoom.")
        return False

    print("Camera adjustment failed after all retries")
    return False


# time.sleep(2)
# scroll_to_zoom(1015, speed=1)