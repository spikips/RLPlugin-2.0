from hueycoatl_projectile import PRAYER_MAP, find_closest_safe_walkable_tile, get_all_gfx_objects, projectile, prayer_schedule
from modules.core.plugin_client import projectiles, gfx, gametick, walkable_tile, player, npc
from modules.npc_data.click_npc import click_closest_npc
from modules.object_data.game_object import click_gameobject, get_game_object_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.utils.select_menu_option import select_menu_option
from hueycoatl_toggle_prayer import toggle_prayer
from modules.utils.camera import camera
import sys
import time
import threading

sys.stdout.reconfigure(encoding='utf-8')
sys.stderr.reconfigure(encoding='utf-8')

# ====================== BODY DEFINITIONS ======================
bodies = [
    {
        "name": "Body 1",
        "tile_offset": (-4, -8),
        "camera": {"pitch": 437, "yaw": 810, "zoom": 589},
        "npc_name": "hueycoatl body"
    },
    {
        "name": "Body 2",
        "tile_offset": (2, -9),
        "camera": {"pitch": 408, "yaw": 167, "zoom": 650},
        "npc_name": "hueycoatl body"
    },
    {
        "name": "Body 3",
        "tile_offset": (-1, -12),
        "camera": {"pitch": 378, "yaw": 128, "zoom": 617},
        "npc_name": "hueycoatl body"
    },
    {
        "name": "Body 4",
        "tile_offset": (-4, -15),
        "camera": {"pitch": 393, "yaw": 477, "zoom": 655},
        "npc_name": "hueycoatl body"
    },
    {
        "name": "Body 5",
        "tile_offset": (-8, -12),
        "camera": {"pitch": 395, "yaw": 523, "zoom": 647},
        "npc_name": "hueycoatl body"
    }
]

# ====================== GATE TILE ======================
gate_tile = get_game_object_tile("55401", radius=20)
print(f"Gate tile: {gate_tile}")

if isinstance(gate_tile, tuple) and len(gate_tile) == 2:
    gate_x, gate_y = gate_tile
else:
    gate_x = gate_tile['x']
    gate_y = gate_tile['y']

# Calculate absolute world tiles
for body in bodies:
    body["tile"] = (
        gate_x + body["tile_offset"][0],
        gate_y + body["tile_offset"][1]
    )
    print(f"{body['name']} tile set to: {body['tile']}")


current_body_index = 0
stop_prayer_thread = threading.Event()

# ====================== COOLDOWNS (prevents spam clicks + instant blue re-check) ======================
blue_tile_cooldown_until = 0
next_action_tick = 0

def prayer_handler():
    """Runs completely independently in the background with exact timing + 5-tick ignore window."""
    print("🚀 Prayer handler thread started (asynchronous)")
    
    for info in prayer_schedule.values():
        info.setdefault('previously_present', False)
        info.setdefault('activate_at', None)
        info.setdefault('deactivate_at', None)
        info.setdefault('ignore_until', 0)

    while not stop_prayer_thread.is_set():
        try:
            tick = gametick()
            current_tick = tick.get('data') if isinstance(tick, dict) and 'data' in tick else tick

            for proj_id, info in prayer_schedule.items():
                is_present = bool(projectile(proj_id))

                if current_tick < info.get('ignore_until', 0):
                    info['previously_present'] = is_present
                    continue

                if is_present and not info['previously_present']:
                    print(f"[Prayer Thread | Tick {current_tick}] → NEW {info['name']} projectile detected → scheduling activation in 5 ticks")
                    info['activate_at'] = current_tick + 5

                if info['activate_at'] is not None and current_tick >= info['activate_at']:
                    print(f"[Prayer Thread | Tick {current_tick}] → ACTIVATING {info['name']}")
                    success = toggle_prayer(info['name'], activate=True)
                    info['deactivate_at'] = current_tick + 2 
                    info['activate_at'] = None

                if info['deactivate_at'] is not None and current_tick >= info['deactivate_at']:
                    print(f"[Prayer Thread | Tick {current_tick}] → DEACTIVATING {info['name']}")
                    success = toggle_prayer(info['name'], activate=False)
                    info['deactivate_at'] = None
                    info['ignore_until'] = current_tick + 5
                    print(f"[Prayer Thread | Tick {current_tick}] → Ignore window active until tick {info['ignore_until']}")

                info['previously_present'] = is_present

            time.sleep(0.05)
        except Exception as e:
            print(f"[Prayer Thread] Error: {e}")
            time.sleep(0.1)

# Start the asynchronous prayer thread
prayer_thread = threading.Thread(target=prayer_handler, daemon=True)
prayer_thread.start()


def attack_body(current_body):
    """Attack with action cooldown to prevent overlapping clicks"""
    global next_action_tick
    tick = gametick()
    current_tick = tick.get('data') if isinstance(tick, dict) and 'data' in tick else tick

    if current_tick < next_action_tick:
        print(f"[Action Cooldown] Skipping attack - too soon after previous action")
        return False

    print(f"Attacking {current_body['name']} at tile {current_body['tile']}")

    npc_data = npc(name=current_body["npc_name"])
    if not npc_data or 'data' not in npc_data or not npc_data['data']:
        print(f"No {current_body['name']} found!")
        return False

    target_tile = current_body["tile"]
    best_npc = None
    best_dist = float('inf')

    for npc_entry in npc_data['data']:
        ntile = npc_entry['tile']
        dist = ((ntile['x'] - target_tile[0]) ** 2 + (ntile['y'] - target_tile[1]) ** 2) ** 0.5
        if dist < best_dist:
            best_dist = dist
            best_npc = npc_entry

    if best_npc and best_dist <= 6:
        mp = best_npc['middle_point']
        mx = mp['x']
        my = mp['y']
        print(f"Found {current_body['name']} → clicking Attack at screen ({mx}, {my})")
        select_menu_option(mx, my, "Attack")
        next_action_tick = current_tick + 2   # short cooldown after each attack
        return True
    else:
        print(f"Could not find {current_body['name']} near target tile (closest was {best_dist:.1f} tiles away)")
        return False


def is_body_alive(current_body) -> bool:
    npc_data = npc(name=current_body["npc_name"])
    if not npc_data or 'data' not in npc_data or not npc_data['data']:
        return False

    target_tile = current_body["tile"]
    for npc_entry in npc_data['data']:
        ntile = npc_entry['tile']
        dist = ((ntile['x'] - target_tile[0]) ** 2 + (ntile['y'] - target_tile[1]) ** 2) ** 0.5
        if dist <= 4:
            return True
    return False


def set_camera_for_body(body):
    cam = body["camera"]
    print(f"[CAMERA] Setting for {body['name']}: pitch={cam['pitch']}, yaw={cam['yaw']}, zoom={cam['zoom']}")
    success = camera(cam["pitch"], cam["yaw"], cam["zoom"])
    if success:
        print(f"✅ Camera set for {body['name']}")
    else:
        print(f"⚠️ Camera adjustment for {body['name']} may not be perfect")
    time.sleep(0.4)

def enter_inside():
    camera(512, 447, 250)
    click_gameobject("55401", "Quick-climb", radius=20)
    wait_till_character_stopped_moving(required_idle_ticks=3)


# ====================== INITIAL SETUP ======================
print("\n=== Starting Hueycoatl script - Engaging Body 1 ===")
enter_inside()
attack_body(bodies[0])
set_camera_for_body(bodies[0])


# ====================== MAIN LOOP ======================
while current_body_index < len(bodies):
    tick = gametick()
    current_tick = tick.get('data') if isinstance(tick, dict) and 'data' in tick else tick
    current_body = bodies[current_body_index]
    print(f"[Main Thread | Tick {current_tick}] Current body: {current_body['name']}")

    # === BLUE TILE EVASION (only if cooldown allows) ===
    if current_tick >= blue_tile_cooldown_until:
        blue_tiles = get_all_gfx_objects(3001, radius=20)

        if blue_tiles:
            print(f"[Main Thread | Tick {current_tick}] BLUE TILES DETECTED! ({len(blue_tiles)} tiles) Waiting 2 ticks...")
            wait_for_next_tick(2)

            blue_tiles = get_all_gfx_objects(3001, radius=20)
            safe_tile = find_closest_safe_walkable_tile(blue_tiles, search_radius=10)

            if safe_tile:
                mp = safe_tile.get('middle_point', {})
                mx = mp.get('x')
                my = mp.get('y')
                print(f"[Main Thread | Tick {current_tick}] SAFE TILE FOUND → Walking to ({mx}, {my})")
                select_menu_option(mx, my, "walk here")

                # Re-engage body
                print(f"Re-engaging {current_body['name']} after blue tile evasion")
                set_camera_for_body(current_body)
                attack_body(current_body)

                # === Wait 5+ ticks after re-attacking before checking blue tiles again ===
                blue_tile_cooldown_until = current_tick + 7
                print(f"[Blue Tile] Cooldown activated until tick {blue_tile_cooldown_until}")
            else:
                print(f"[Main Thread | Tick {current_tick}] No safe walkable tile found!")

    # === CHECK IF CURRENT BODY IS DEAD ===
    if not is_body_alive(current_body):
        print(f"✅ {current_body['name']} is dead! Advancing to next body...")
        current_body_index += 1
        if current_body_index < len(bodies):
            next_body = bodies[current_body_index]
            print(f"Engaging {next_body['name']}")
            set_camera_for_body(next_body)
            attack_body(next_body)

    wait_for_next_tick()


wait_for_next_tick(8)

# 1
for i in range(10):
    if click_minimap_tile(1515, 3290, rand_x=2, rand_y=2, target_zoom=2.0):
        print("clicked minimap tile (1515, 3290)")
        if wait_till_character_stopped_moving():
            break
    wait_for_next_tick()
    if i == 9:
        exit("Failed to click minimap tile (1515, 3290)")


# Cleanup
stop_prayer_thread.set()
prayer_thread.join(timeout=1.0)
print("🎉 All 5 bodies defeated! Hueycoatl fight complete.")
print("Prayer handler thread stopped.")