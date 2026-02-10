# shade.py
# Script for automating Loar Shade slayer task (no cannon, no movement).
# Behavior:
# - Keeps Protect from Melee prayer active with dynamic potion drinking.
# - If aggro: Stay put (fight normally).
# - If no reachable aggro → advanced swoop reset:
#   - Tries to attack the closest on-screen Loar Shadow or Loar Shade (in priority order)
#   - Uses existing click_closest_npc() which already handles on-screen/valid clicks safely
#   - After successful attack click, monitors for up to 20 ticks:
#     - If player leaves the area → minimap click fallback tile
#     - If the targeted NPC leaves the area or disappears → break monitoring and re-swoop
#     - Refreshes every tick
#   - If reachable aggro regained at any point → success, return to normal fighting
# - On task completion → navigate to Vannaka

import time
import random
import math

# Core imports
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import player, inventory, npc_agro, slayer_task_remaining, npc

# Utils imports
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from modules.utils.check_if_in_area import point_in_polygon


# === GLOBAL CONSTANTS ===
AREA_POLYGON = [
    (3495,3323),
    (3498,3323),
    (3499,3322),
    (3502,3322),
    (3503,3323),
    (3512,3323),
    (3518,3317),
    (3518,3314),
    (3516,3312),
    (3513,3311),
    (3510,3309),
    (3503,3309),
    (3500,3310),
    (3496,3311),
    (3495,3313),
    (3492,3315),
    (3491,3319),
    (3495,3323)
]

FALLBACK_TILE = (3506, 3312, 0)  # Minimap click when player leaves area

NPC_NAMES = ["Loar Shadow", "Loar Shade"]  # Priority order - tries Shadow first, then Shade

SWOOP_MAX_ATTEMPTS = 100

# Prayer potion drinking (unchanged)
def check_prayer_level():
    p_data = player(prayer=True)
    if not p_data or 'data' not in p_data:
        return 100
    return p_data['data'].get('prayer', 100)

def has_prayer_potion():
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data:
        return False
    for item in inv_data['data']:
        name = item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            return True
    return False

def drink_prayer_potion():
    from modules.core.window_utils import runelite_window
    from modules.core.mouse_control import move
    inv_data = inventory()
    if not inv_data or 'data' not in inv_data or not inv_data['data']:
        return False
    for inv_item in inv_data['data']:
        name = inv_item.get('name', '').strip()
        if name.startswith('Prayer potion('):
            mp = inv_item['middle_point']
            sx, sy = runelite_window(mp['x'], mp['y'])
            move(sx, sy, fast=True, sleep=True, button='left')
            print(f"Drank {name}")
            wait_for_next_tick(1)
            return True
    return False

# Aggro check (unchanged)
def is_aggroed():
    agro_data = npc_agro()
    
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected.")
        return False
    
    # Fixed key to match API ('canReach' camelCase instead of 'canreach')
    reachable = any(npc.get('canReach', False) for npc in agro_data['aggressiveNpcs'])
    
    if reachable:
        print("Aggro detected (reachable)")
        wait_for_next_tick(5)
        return True
    
    print("Aggressive NPCs present but none reachable - waiting 1 tick to recheck.")
    
    agro_data = npc_agro()
    
    if agro_data and agro_data.get('aggressiveNpcs'):
        reachable = any(npc.get('canReach', False) for npc in agro_data['aggressiveNpcs'])
        if reachable:
            print("Aggro now reachable after wait.")
            return True
    

    print("Still no reachable aggro after wait - starting swoop reset.")
    return False

def swoop_reset():
    print("No reachable aggro - starting advanced swoop reset")
    
    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print(f"\n=== Swoop attempt {attempt + 1} ===")
        
        # Player position check - return to area if needed
        player_data = player(location=True)
        if not player_data or 'data' not in player_data:
            print("Failed to get player location data")
            wait_for_next_tick(3)
            continue
        loc = player_data['data'].get('location', {})
        px, py = loc.get('x', 0), loc.get('y', 0)
        player_inside = point_in_polygon(px, py, AREA_POLYGON)
        print(f"Current player position: ({px}, {py}) - inside polygon: {player_inside}")
        
        if not player_inside:
            print(f"Player outside area ({px}, {py}) - clicking fallback tile")
            click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
            wait_till_character_stopped_moving()
            wait_for_next_tick(1)
            continue
        
        # Try to attack closest NPC from our list (priority order)
        # We now attack the closest even if outside - the area safeguards will prevent leaving
        attacked_name = None
        target_id = None
        
        for name in NPC_NAMES:
            print(f"\nChecking for {name}(s)...")
            npc_data = npc(name=name, tile=True)
            if npc_data and 'data' in npc_data and npc_data['data']:
                print(f"Found {len(npc_data['data'])} {name}(s) on screen:")
                for idx, n in enumerate(npc_data['data']):
                    t_tile = n.get('tile', {})
                    tx, ty = t_tile.get('x', 0), t_tile.get('y', 0)
                    npc_inside = point_in_polygon(tx, ty, AREA_POLYGON)
                    rank = "closest" if idx == 0 else f"#{idx + 1}"
                    print(f"  {rank}: {name} (ID: {n.get('id')}) at ({tx}, {ty}) - inside polygon: {npc_inside}")
                
                # Always attempt to attack the closest of this type if any exist
                closest_npc = npc_data['data'][0]
                t_tile = closest_npc.get('tile', {})
                tx, ty = t_tile.get('x', 0), t_tile.get('y', 0)
                closest_inside = point_in_polygon(tx, ty, AREA_POLYGON)
                print(f"Closest {name} is {'INSIDE' if closest_inside else 'OUTSIDE'} area ({tx},{ty}) - attempting attack anyway")
                
                if click_closest_npc(name, option='Attack', max_attempts=5):
                    print(f"SUCCESS: Attacked closest {name} (ID: {closest_npc.get('id')}) at ({tx},{ty})")
                    attacked_name = name
                    target_id = closest_npc.get('id')
                    break
                else:
                    print(f"FAILED to click closest {name}")
            else:
                print(f"No {name} found on screen")
        
        if not attacked_name:
            print("No Loar Shadow or Shade found on screen at all - waiting and retrying")
            wait_for_next_tick(1)
            continue
        
        print("\nWaiting for character to stop moving with area safeguard...")
        
        # Get initial position
        player_data = player(location=True)
        if player_data and 'data' in player_data:
            prev_x = player_data['data'].get('location', {}).get('x', 0)
            prev_y = player_data['data'].get('location', {}).get('y', 0)
        else:
            prev_x, prev_y = 0, 0
        
        consecutive_same_pos = 0
        corrected_during_wait = False
        
        for wait_tick in range(50):
            wait_for_next_tick(1)
            
            player_data = player(location=True)
            if not player_data or 'data' not in player_data:
                continue
            
            loc = player_data['data'].get('location', {})
            curr_x = loc.get('x', 0)
            curr_y = loc.get('y', 0)
            
            print(f"  Wait tick {wait_tick + 1}: Player at ({curr_x}, {curr_y}) - inside: {point_in_polygon(curr_x, curr_y, AREA_POLYGON)}")
            
            if not point_in_polygon(curr_x, curr_y, AREA_POLYGON):
                print(f"Player straying outside during approach ({curr_x},{curr_y}) - correcting to fallback tile")
                click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
                wait_till_character_stopped_moving()
                wait_for_next_tick(1)
                corrected_during_wait = True
                break
            
            if curr_x == prev_x and curr_y == prev_y:
                consecutive_same_pos += 1
                if consecutive_same_pos >= 3:
                    print("Character has stopped moving (position stable for 3 ticks).")
                    break
            else:
                consecutive_same_pos = 0
            
            prev_x = curr_x
            prev_y = curr_y
        
        else:
            print("Timeout while waiting for character to stop moving - proceeding anyway")
        
        print("Entering 20-tick monitoring phase...")
        
        for monitor_tick in range(20):
            wait_for_next_tick(1)
            print(f"  Monitor tick {monitor_tick + 1}: Checking aggro/target/player status")
            
            player_data = player(location=True)
            if player_data and 'data' in player_data:
                loc = player_data['data'].get('location', {})
                px, py = loc.get('x', 0), loc.get('y', 0)
                if not point_in_polygon(px, py, AREA_POLYGON):
                    print(f"Player left area during monitoring ({px}, {py}) - returning to fallback")
                    click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
                    wait_till_character_stopped_moving()
                    break
            
            # if target_id:
            #     target_data = npc(id=str(target_id), tile=True)
            #     if not target_data or 'data' not in target_data or not target_data['data']:
            #         print("Target NPC disappeared - re-swooping")
            #         break
            #     t_tile = target_data['data'][0].get('tile', {})
            #     tx, ty = t_tile.get('x', 0), t_tile.get('y', 0)
            #     print(f"  Target NPC (closest of type) still at ({tx}, {ty}) - inside: {point_in_polygon(tx, ty, AREA_POLYGON)}")
                # if not point_in_polygon(tx, ty, AREA_POLYGON):
                #     print(f"Target NPC left area ({tx}, {ty}) - re-swooping")
                #     break
            
            if is_aggroed():
                print("Reachable aggro regained - swoop successful")
                wait_for_next_tick(8)
                return True
        
        print("Monitoring ended without regaining aggro - continuing to next swoop attempt")
    
    print("Swoop exhausted max attempts")
    return False

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting up camera...")
    camera(
        pitch=random.randint(450, 512),
        yaw=random.randint(0, 150),
        zoom=random.randint(200, 280)
    )

    prayer_threshold = random.randint(15, 25)
    print(f"Initial prayer drink threshold: {prayer_threshold}")

    print("Starting Loar Shade slayer task - stay in area, advanced swoop when no reachable aggro.")

    while True:
        task_remaining = slayer_task_remaining()
        print(f"Slayer task remaining: {task_remaining}")
        if task_remaining == 0:
            break

        toggle_prayer('PROTECT_FROM_MELEE', activate=True)
        current_prayer = check_prayer_level()
        if current_prayer <= prayer_threshold:
            if has_prayer_potion():
                drink_prayer_potion()
                print(f"Drank prayer potion (prayer {current_prayer} <= {prayer_threshold})")
                prayer_threshold = random.randint(15, 25)
                print(f"New prayer threshold: {prayer_threshold}")
            else:
                print("Prayer low, no potion available.")

        if is_aggroed():
            print("Aggro active - fighting normally.")
        else:
            swoop_reset()


if __name__ == "__main__":
    main()