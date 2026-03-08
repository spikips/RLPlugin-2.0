# shade.py
# Refactored + improved aggro filter: ONLY Loar Shadow / Loar Shade with canReach=True count as aggro
# Ignores ghosts/other NPCs. Swoop only when no reachable Loar. Same behavior: protect melee, dynamic prayer, area safeguard, camera random

import time
import random

# Core
from modules.core.window_utils import focus_runelite_window
from modules.core.plugin_client import player, npc_agro, npc

# Utils
from modules.utils.humanlike_interact import perform_humanlike_interaction
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.npc_data.click_npc import click_closest_npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.camera import camera
from modules.utils.check_if_in_area import point_in_polygon

# Shared utils
from scripts.combat.slayer.utils.slayer_task_utils import (
    manage_prayer,
    get_slayer_task_remaining,
)

# Constants
AREA_POLYGON = [
    (3495,3323), (3498,3323), (3499,3322), (3502,3322), (3503,3323),
    (3512,3323), (3518,3317), (3518,3314), (3516,3312), (3513,3311),
    (3510,3309), (3503,3309), (3500,3310), (3496,3311), (3495,3313),
    (3492,3315), (3491,3319), (3495,3323)
]
FALLBACK_TILE = (3506, 3312, 0)
NPC_NAMES = ["Loar Shadow", "Loar Shade"]
SWOOP_MAX_ATTEMPTS = 100

def is_aggroed():
    """ONLY Loar Shadow or Loar Shade with canReach=True count as aggro."""
    agro_data = npc_agro()
    if not agro_data or not agro_data.get('aggressiveNpcs'):
        print("No aggressive NPCs detected.")
        return False

    target_names = {"Loar Shadow", "Loar Shade"}
    for n in agro_data['aggressiveNpcs']:
        if n.get('name') in target_names and n.get('canReach', False):
            print("Aggro detected (reachable Loar Shadow/Shade)")
            wait_for_next_tick(5)
            return True

    print("No reachable Loar Shadow/Shade - waiting 1 tick to recheck.")

    agro_data = npc_agro()
    if agro_data and agro_data.get('aggressiveNpcs'):
        for n in agro_data['aggressiveNpcs']:
            if n.get('name') in target_names and n.get('canReach', False):
                print("Aggro now reachable after wait.")
                return True

    print("Still no reachable Loar - starting swoop reset.")
    return False

def swoop_reset():
    """Exact original swoop logic (only attacks Loar Shadow/Shade)."""
    print("No reachable aggro - starting advanced swoop reset")

    for attempt in range(SWOOP_MAX_ATTEMPTS):
        print("\n=== Swoop attempt {} ===".format(attempt + 1))

        player_data = player(location=True)
        if not player_data or 'data' not in player_data:
            print("Failed to get player location data")
            wait_for_next_tick(3)
            continue
        loc = player_data['data'].get('location', {})
        px, py = loc.get('x', 0), loc.get('y', 0)
        player_inside = point_in_polygon(px, py, AREA_POLYGON)
        print("Current player position: ({}, {}) - inside polygon: {}".format(px, py, player_inside))

        if not player_inside:
            print("Player outside area - returning to fallback tile")
            click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
            wait_till_character_stopped_moving()
            wait_for_next_tick(1)
            continue

        target_clicked = False
        for name in NPC_NAMES:
            if click_closest_npc(name, option='Attack', max_attempts=3):
                print("Successfully clicked closest {}".format(name))
                target_clicked = True
                break

        if not target_clicked:
            print("Failed to find/click any target NPC - retrying next attempt")
            wait_for_next_tick(1)
            continue

        print("Waiting for character to stop moving after swoop click...")

        prev_x = prev_y = 0
        if player_data and 'data' in player_data:
            loc = player_data['data'].get('location', {})
            prev_x = loc.get('x', 0)
            prev_y = loc.get('y', 0)

        consecutive_same_pos = 0
        for wait_tick in range(50):
            wait_for_next_tick(1)
            player_data = player(location=True)
            if not player_data or 'data' not in player_data:
                continue
            loc = player_data['data'].get('location', {})
            curr_x = loc.get('x', 0)
            curr_y = loc.get('y', 0)

            print("  Wait tick {}: Player at ({}, {}) - inside: {}".format(
                wait_tick + 1, curr_x, curr_y, point_in_polygon(curr_x, curr_y, AREA_POLYGON)))

            if not point_in_polygon(curr_x, curr_y, AREA_POLYGON):
                print("Player straying outside - correcting to fallback tile")
                click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
                wait_till_character_stopped_moving()
                wait_for_next_tick(1)
                break

            if curr_x == prev_x and curr_y == prev_y:
                consecutive_same_pos += 1
                if consecutive_same_pos >= 3:
                    print("Character stopped moving.")
                    break
            else:
                consecutive_same_pos = 0
            prev_x = curr_x
            prev_y = curr_y

        print("Entering 20-tick monitoring phase...")

        for monitor_tick in range(20):
            wait_for_next_tick(1)
            print("  Monitor tick {}: Checking aggro".format(monitor_tick + 1))

            player_data = player(location=True)
            if player_data and 'data' in player_data:
                loc = player_data['data'].get('location', {})
                px, py = loc.get('x', 0), loc.get('y', 0)
                if not point_in_polygon(px, py, AREA_POLYGON):
                    print("Player left area - returning to fallback")
                    click_minimap_tile(FALLBACK_TILE[0], FALLBACK_TILE[1])
                    wait_till_character_stopped_moving()
                    break

            if is_aggroed():
                print("Reachable aggro regained - swoop successful")
                wait_for_next_tick(8)
                return True

        print("No aggro regained - next swoop attempt")

    print("Swoop exhausted max attempts")
    return False

def main():
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return

    from modules.utils.logout import check_login_state_and_login
    check_login_state_and_login()

    print("Setting up camera...")
    camera(
        pitch=random.randint(450, 512),
        yaw=random.randint(0, 150),
        zoom=random.randint(200, 280)
    )

    prayer_threshold = random.randint(15, 25)
    print("Initial prayer threshold: {}".format(prayer_threshold))

    print("Loar Shade task started.")

    while True:
        task_remaining = get_slayer_task_remaining()
        print("Slayer task remaining: {}".format(task_remaining))
        if task_remaining == 0:
            break

        toggle_prayer('PROTECT_FROM_MELEE', activate=True)

        new_p = manage_prayer(prayer_threshold)
        if new_p is not None:
            prayer_threshold = new_p

        if random.randint(1, 100) <= 1:  # 1% chance to perform humanlike interaction each loop
            perform_humanlike_interaction(low=1, peak=2, high=10)

        if is_aggroed():
            print("Aggro active - fighting normally.")
        else:
            swoop_reset()

def run():
    main()

if __name__ == "__main__":
    run()