import time
import random
from datetime import datetime, timedelta
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.object_data.game_object import get_closest_game_object
from modules.utils.select_menu_option import select_menu_option
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import player, pick, game_state
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window
from modules.widgets.widget import click_widget

rl_x, rl_y = runelite_window(0, 0)

def point_in_polygon(x, y, vertices):
    n = len(vertices)
    inside = False
    j = n - 1
    for i in range(n):
        xi, yi = vertices[i]
        xj, yj = vertices[j]
        if (xi, yi) == (x, y) or (xj, yj) == (x, y):
            return True
        if min(yi, yj) <= y <= max(yi, yj) and min(xi, xj) <= x <= max(xi, xj):
            if (xj - xi) * (y - yi) == (yj - yi) * (x - xi):
                return True
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-10) + xi):
            inside = not inside
        j = i
    return inside

def random_camera_tweak(pass_random=False):
    if not pass_random and random.random() > 0.05:
        return
    
    print("Random camera tweak triggered")
    
    camera_data = player(camera=True).get('data', {}).get('camera', {})
    current_zoom = camera_data.get('zoom', 'unknown')
    current_pitch = camera_data.get('pitch', 'unknown')
    current_yaw = camera_data.get('yaw', 'unknown')
    print(f"Before tweak - Zoom: {current_zoom}, Pitch: {current_pitch}, Yaw: {current_yaw}")
    
    pitch = random.randint(400, 512)
    yaw = random.randint(0, 500) if random.random() < 0.5 else random.randint(1548, 2048)
    zoom = random.randint(150, 250)
    
    camera(pitch, yaw, zoom, speed=1)
    
    final_data = player(camera=True).get('data', {}).get('camera', {})
    print(f"After tweak - Zoom: {final_data.get('zoom', 'unknown')}, "
          f"Pitch: {final_data.get('pitch', 'unknown')}, Yaw: {final_data.get('yaw', 'unknown')}")

def loot_marks_in_current_area(vertices, plane, tile_radius=15, item_name="Mark of grace"):
    p_data = player(location=True)
    if not p_data or 'data' not in p_data:
        print("Failed to get player location for looting.")
        return 0
    
    loc = p_data['data'].get('location', {})
    player_x = loc.get('x')
    player_y = loc.get('y')
    if player_x is None or player_y is None:
        print("Invalid player coordinates for looting.")
        return 0

    pick_data = pick(player_x, player_y, size=tile_radius, item=item_name)
    if not pick_data or 'data' not in pick_data or 'items' not in pick_data['data']:
        print("No marks found or failed to query ground items.")
        return 0

    items = pick_data['data']['items']
    if not items:
        return 0

    picked = 0
    for item in items:
        tile = item.get('tile', {})
        item_x = tile.get('x')
        item_y = tile.get('y')
        item_plane = tile.get('plane')

        print(f"DEBUG: Found mark at tile ({item_x}, {item_y}, plane {item_plane})")

        if item_plane != plane:
            print(f"    Skipped: mark is on different plane (player on plane {plane}, mark on {item_plane})")
            continue

        if not point_in_polygon(item_x, item_y, vertices):
            print("    Skipped: mark tile is outside current area polygon")
            continue

        mp = item.get('middle_point', {})
        mx, my = mp.get('x'), mp.get('y')

        if mx is not None and my is not None:
            print(f"    Looting mark at tile ({item_x}, {item_y}, {item_plane}) (screen: {mx},{my})")
            success = select_menu_option(mx, my, "Take")  # Change to "Pick up" if needed
            if success:
                picked += 1
                print("    Successfully looted")
                time.sleep(random.uniform(0.5, 1.0))
            else:
                print("    Failed to select 'Take' on mark")
        else:
            print("    No valid screen position for mark")

    return picked

def check_login_state_and_login():
    """Check login state and perform login sequence if at login screen."""
    if game_state().get('data') == "LOGIN_SCREEN":
        mouse(391 + rl_x, 303 + rl_y, button="left", fast=True, sleep=True)
        time.sleep(random.uniform(0.22, 0.3))
        mouse(391 + rl_x, 263 + rl_y, button="left", fast=True, sleep=True)

        # Poll for login states, up to 15 seconds total
        start_time_poll = time.time()
        first_logged_in = False
        while time.time() - start_time_poll < 15:
            state = game_state().get('data')
            print(f"Main Menu Data: {{'data': '{state}'}}")
            if state == 'LOGGED_IN' and not first_logged_in:
                time.sleep(0.4)  # Wait 0.4s before click
                mouse(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
                time.sleep(0.6)  # Wait 0.6s after click
                print("Clicked post-login button after first LOGGED_IN")
                first_logged_in = True
                return True  # Exit early after successful login and clicks
            time.sleep(0.1)
        print("Login timed out after 15 seconds")
        exit("Failed to log back in")
    return False

def logout_and_break(break_minutes):
    """Logout, take a break for specified minutes, and log back in. Prints timestamps and duration."""
    print("Initiating logout for break")
    logged_out = False

    # clicks logout widget
    click_widget(35913786, rand_x=10, rand_y=10)

    time.sleep(random.uniform(0.22, 0.25))
    tries = 0
    while not logged_out:
        # Logout clicks
        logout_1 = click_widget(11927564)
        if not logout_1:
            click_widget(4522009)
        
        # Poll for up to 2 seconds
        start_poll = time.time()
        while time.time() - start_poll < 2:
            if game_state().get('data') == "LOGIN_SCREEN":
                print("Logged out successfully")
                logged_out = True
                break
            time.sleep(0.1)
        
        if not logged_out:
            tries += 1
            print(f"Logout not detected, retrying...", {tries})

    # Calculate and print times
    break_seconds = break_minutes * 60
    start_time = datetime.now()
    resume_time = start_time + timedelta(seconds=break_seconds)
    duration = timedelta(seconds=break_seconds)
    print(f"Break started at: {start_time.strftime('%H:%M:%S')}")
    print(f"Script will resume at: {resume_time.strftime('%H:%M:%S')}")
    print(f"Sleep duration: {str(duration).split('.')[0]}")  # hh:mm:ss format

    time.sleep(break_seconds)

    mouse(391 + rl_x, 303 + rl_y, button="left", fast=True, sleep=True)
    time.sleep(random.uniform(0.22, 0.3))
    mouse(391 + rl_x, 263 + rl_y, button="left", fast=True, sleep=True)

    # Poll for login states, up to 15 seconds total
    start_time_poll = time.time()
    first_logged_in = False
    while time.time() - start_time_poll < 15:
        state = game_state().get('data')
        print(f"Main Menu Data: {{'data': '{state}'}}")
        if state == 'LOGGED_IN' and not first_logged_in:
            time.sleep(0.4)  # Wait 0.4s before click
            mouse(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
            time.sleep(0.6)  # Wait 0.6s after click
            print("Clicked post-login button after first LOGGED_IN")
            first_logged_in = True
            return True  # Exit early after successful login and clicks
        time.sleep(0.1)
    print("Login timed out after 15 seconds")
    exit("Failed to log back in")

def ensure_logged_in():
    state = game_state().get('data')
    if state != "LOGGED_IN":
        print(f"Detected not logged in (state: {state}). Attempting login...")
        return check_login_state_and_login()
    return False

def run_canifis_agility():
    focus_runelite_window()
    
    # Check login at start
    ensure_logged_in()
    
    areas = [
        {"vertices": [(3494,3490), (3487,3489), (3487,3481), (3489,3472), 
                      (3505,3473), (3519,3477), (3516,3487), (3512,3494),
                      (3507,3499), (3494,3497)],
         "plane": 0, "obj_id": "14843", "action": "Climb"},
        {"vertices": [(3503, 3499), (3503, 3490), (3513, 3490), (3513, 3499), (3503, 3499)],
         "plane": 2, "obj_id": "14844", "action": "Jump"},
        {"vertices": [(3495, 3508), (3495, 3501), (3505, 3502), (3505, 3508), (3496, 3508)],
         "plane": 2, "obj_id": "14845", "action": "Jump"},
        {"vertices": [(3484, 3503), (3484, 3496), (3494, 3496), (3494, 3506), (3486, 3506), (3484, 3503)],
         "plane": 2, "obj_id": "14848", "action": "Jump"},
        {"vertices": [(3473, 3500), (3473, 3489), (3482, 3489), (3481, 3502), (3473, 3500)],
         "plane": 3, "obj_id": "14846", "action": "Jump"},
        {"vertices": [(3476, 3488), (3476, 3479), (3482, 3479), (3482, 3483), (3485, 3484), (3485, 3488), (3476, 3488)],
         "plane": 2, "obj_id": "14894", "action": "Vault"},
        {"vertices": [(3486, 3479), (3487, 3466), (3506, 3466), (3505, 3478), (3498, 3480), (3489, 3480), (3486, 3479)],
         "plane": 3, "obj_id": "14847", "action": "Jump"},
        {"vertices": [(3507, 3484), (3507, 3472), (3517, 3472), (3517, 3484), (3507, 3484)],
         "plane": 2, "obj_id": "14897", "action": "Jump"}
    ]
    
    recovery_vertices = [(3480, 3502), (3480, 3489), (3495, 3488), (3501, 3494), (3490, 3504), (3480, 3502)]
    recovery_target_tile = (3507, 3486)
    
    laps_completed = 0
    
    print("Starting Canifis Rooftop Agility script...")
    
    # Set initial break time
    next_break_time = time.time() + random.uniform(25 * 60, 50 * 60)
    
    while True:
        # Check if logged in before proceeding
        ensure_logged_in()
        
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to get player location")
            time.sleep(0.6)
            continue
        
        loc = pl_data['data']['location']
        px, py, pplane = loc['x'], loc['y'], loc['plane']
        current_tile = (px, py, pplane)
        
        if pplane == 0 and point_in_polygon(px, py, recovery_vertices):
            print(f"Fallen in recovery area at {current_tile} - returning to start")
            recovered = False
            for _ in range(8):  # Try up to 8 times
                if click_minimap_tile(recovery_target_tile[0], recovery_target_tile[1], rand_x=3, rand_y=3):
                    random_camera_tweak()
                    wait_till_character_stopped_moving()
                    recovered = True
                    break
            if not recovered:
                print("Recovery failed after 8 attempts")
                break
            continue
        
        current_area = None
        for area in areas:
            if pplane == area["plane"] and point_in_polygon(px, py, area["vertices"]):
                current_area = area
                break
        
        if current_area is None:
            print(f"Unknown position: {current_tile}")
            time.sleep(1.5)
            continue
        
        obj_id = current_area["obj_id"]
        action = current_area["action"]
        print(f"\nIn area for obstacle {obj_id} - {action} (tile {current_tile})")
        
        obj = get_closest_game_object(object_identifier=obj_id, radius=60)
        if not obj or 'middle_point' not in obj:
            print("    Obstacle not found or not on screen")
            time.sleep(0.8)
            random_camera_tweak(pass_random=True)
            continue
        
        mp = obj['middle_point']
        success = select_menu_option(mp['x'], mp['y'], action)
        
        if not success:
            print(f"    Failed to select '{action}'")
            time.sleep(0.7)
            continue
        
        print(f"    Clicked '{action}' on {obj_id}")
        
        time.sleep(random.uniform(0.3, 0.6))
        
        initial_anim = -1
        pl_data = player(location=True, animation=True)
        if pl_data and 'data' in pl_data and 'animation' in pl_data['data']:
            initial_anim = pl_data['data']['animation']
        
        print("    Waiting for obstacle animation to begin...")
        anim_started = False
        start_time = time.time()
        while time.time() - start_time < 8:
            pl_data = player(location=True, animation=True)
            if not pl_data or 'data' not in pl_data:
                time.sleep(0.2)
                continue
                
            anim = pl_data['data'].get('animation', -1)
            if anim != -1 and anim != initial_anim:
                print(f"    Animation started: {anim}")
                anim_started = True
                break
            time.sleep(0.15)
        
        if not anim_started:
            print("    Warning: Animation did not start within timeout")
            time.sleep(1.0)
        
        print("    Waiting for obstacle action to finish...")

        finish_timeout = time.time() + 12
        performed = False
        target_time = None  # Will be set only if we decide to schedule an interaction

        # Decide whether to schedule a humanlike interaction (8% chance)
        if random.random() < 0.1:  # 10% chance
            delay = random.uniform(0.5, 4)
            target_time = time.time() + delay
            print(f"    Scheduled humanlike interaction in {delay:.2f}s")

        while time.time() < finish_timeout:
            pl_data = player(location=True, animation=True)

            if target_time is not None and time.time() >= target_time and not performed:
                print(f"    Executing humanlike interaction (scheduled time reached)")
                perform_humanlike_interaction()
                performed = True

            if not pl_data or 'data' not in pl_data:
                time.sleep(0.1)
                continue
                
            anim = pl_data['data'].get('animation', -1)
            if anim == -1:
                print("    Action finished (animation back to -1)")
                if random.random() < 0.1:  # 10% chance to sleep
                    time_to_sleep = random.triangular(1, 6, 300)  # mode at 3 seconds
                    print(f"    Waiting additional {time_to_sleep:.2f}s to mimic human pause")
                    time.sleep(time_to_sleep)
                break
                
            time.sleep(random.uniform(0.05, 0.15))
        
        if time.time() >= finish_timeout:
            print("    Warning: Timeout waiting for animation to finish")
        
        time.sleep(random.uniform(0.4, 0.9))
        random_camera_tweak()

        # Re-fetch player location AFTER obstacle to get updated plane/position
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to re-fetch player location after obstacle")
            time.sleep(0.6)
            continue

        loc = pl_data['data']['location']
        px, py, pplane = loc['x'], loc['y'], loc['plane']

        # Re-determine current area with updated position/plane
        current_area = None
        for area in areas:
            if pplane == area["plane"] and point_in_polygon(px, py, area["vertices"]):
                current_area = area
                break

        if current_area is None:
            print(f"Unknown position after obstacle: ({px}, {py}, {pplane})")
            time.sleep(1.5)
            continue

        # Debug prints before looting

        print(f"DEBUG: Current area: {obj_id}, plane: {pplane}")
        print(f"DEBUG: Vertices: {current_area['vertices']}")

        # Lap complete check
        if obj_id == "14897":
            laps_completed += 1
            print(f"Lap completed! Total laps: {laps_completed}")

            # Check for break after lap
            if time.time() >= next_break_time:
                break_duration = random.uniform(15, 45)
                print(f"Active time exceeded. Taking break for {break_duration:.2f} minutes.")
                logout_and_break(break_duration)
                # Reset next break time after logging back in
                next_break_time = time.time() + random.uniform(25 * 60, 50 * 60)
                # Ensure logged in after break (redundant but safe)
                ensure_logged_in()

            if random.random() < 0.1:  # 10% chance to sleep
                time_to_sleep = random.triangular(1, 25, 300)  # mode at 3 seconds
                print(f"    Waiting additional {time_to_sleep:.2f}s to mimic human pause")
                time.sleep(time_to_sleep)

            perform_humanlike_interaction()
            random_camera_tweak()

        # Loot marks only in current area (now with updated plane)
        print(f"    Checking for Mark of grace in current area (plane {pplane})...")
        marks_picked = loot_marks_in_current_area(
            vertices=current_area["vertices"],
            plane=pplane,
            tile_radius=15,
            item_name="Mark of grace"
        )
        if marks_picked > 0:
            print(f"Picked up {marks_picked} Mark(s) of grace")
            wait_till_character_stopped_moving(required_idle_ticks=1)
            time.sleep(random.uniform(0.6, 1.2))
            random_camera_tweak()
        else:
            print("    No Mark of grace found in current area")


# if __name__ == "__main__":
print("Starting Canifis Rooftop Agility Script")
focus_runelite_window()
check_login_state_and_login()
run_canifis_agility()