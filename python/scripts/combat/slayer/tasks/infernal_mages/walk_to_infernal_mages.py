# 1
import time
from modules.object_data.game_object import click_gameobject
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.camera import camera
from modules.utils.click_tile import click_tile
from modules.utils.inventory import click_inventory
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.widgets.widget import click_widget, click_widget_child
from modules.utils.click_minimap_tile import click_minimap_tile

from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear

def go_to_bank():
    target_gear = get_target_gear()

    # if "Ancient mitre" in target_gear:
    #     target_gear.remove("Ancient mitre")
    #     target_gear.append("Earmuffs")
    #     print("Overridden Ancient mitre → Earmuffs for Infernal Mages task")
    # else:
    #     # Fallback: just add Earmuffs if mitre wasn't there (safety)
    #     target_gear.append("Earmuffs")
    #     print("Added Earmuffs (no Ancient mitre found in gear list)")


    target_inventory = {
        "Prayer potion": 8,
        "Amulet of glory": 1,
        "Ring of dueling": 2,
        "salve graveyard teleport": 1
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
    ensure_correct_combat_style()
    
def walk_to_infernal_mages():
    # 4
    for i in range(5):
        if click_inventory('salve graveyard teleport', action='break', hover_only=False):
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click inventory item (Salve graveyard teleport, Break)")


    # 2
    for i in range(10):
        if click_minimap_tile(3444, 3494, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3444, 3494)")
            # 7
            for i in range(3):
                if camera(pitch=345, yaw=2038, zoom=265, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3444, 3494)")

    # 3
    for i in range(10):
        if click_minimap_tile(3440, 3509, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3440, 3509)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3440, 3509)")

    # 4
    for i in range(10):
        if click_minimap_tile(3442, 3531, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3428, 3532)")
            if wait_till_character_stopped_moving():
                wait_for_next_tick(2)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3428, 3532)")


    # 9
    # Object click: staircase -> Climb-up
    for i in range(5):
        if click_gameobject("57679", 'Climb-through', tile=(3443, 3532), radius=20):
            wait_for_next_tick(1)
            for _ in range(5):
                if wait_until_at_tile(3444, 3533, timeout_seconds=5):
                    wait_for_next_tick(3)
                    break
                wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (broken window, Climb-through)")


    for i in range(5):
        if click_gameobject("2114", 'Climb-up', tile=(3436, 3538), radius=20):
            wait_till_character_stopped_moving(required_idle_ticks=2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (staircase, Climb-up)")

    # 10
    for i in range(10):
        if click_minimap_tile(3444, 3566, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3444, 3566)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3444, 3566)")


def hop_if_players_nearby():
    hop_tile = (3444, 3566, 0)
    stand_tile = (3444, 3566, 0)

    # hop until empty world
    max_hop_attempts = 15  # Safety limit to avoid infinite hopping
    for hop_attempt in range(max_hop_attempts):
        print(f"Checking for nearby players (attempt {hop_attempt + 1}/{max_hop_attempts})...")
        
        players_detected = check_for_players(radius=10, max_wait_ticks=2)
        
        if not players_detected:
            print("No players detected in 10 tile radius -> safe spot")
            break

        click_minimap_tile(hop_tile[0], hop_tile[1], target_zoom=2.0)
        wait_till_character_stopped_moving(required_idle_ticks=2)
        wait_for_next_tick(8)


        print("Players detected -> hopping to new P2P world")
        if hop_to_random_world('p2p'):
            print("hopped, rechecking")
            wait_for_tick(3)
            continue

        players_detected = check_for_players(radius=10, max_wait_ticks=2)

        if not players_detected:
            click_minimap_tile(stand_tile[0], stand_tile[1], target_zoom=2.0)
            wait_till_character_stopped_moving(required_idle_ticks=2)
            break


def run():
    go_to_bank()
    walk_to_infernal_mages()
    hop_if_players_nearby()
    print("Navigation complete - ready for fighting.")

if __name__ == "__main__":
    run()
