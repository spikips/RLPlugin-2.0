# 1
import time
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
from modules.player_data.tile_change import wait_for_tile_change
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

    target_inventory = {
        "Prayer potion": 5,
        "Games necklace": 1,
        "Amulet of glory": 1,
        "Ring of dueling": 2,
        "Cannon barrels": 1,
        "Cannon furnace": 1,
        "Cannon base": 1,
        "Cannon stand": 1,
        "Steel cannonball": "all",
        "salve graveyard teleport": 1
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
    ensure_correct_combat_style()

def walk_to_ghouls():
    for i in range(5):
        if click_widget_child('35913797', sprite_id=None, hidden=None, child_index=5, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (prayer) via child")

    # 4
    for i in range(5):
        if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to activate prayer (protect from melee)")

    # 4
    for i in range(5):
        if click_inventory('salve graveyard teleport', action='break', hover_only=False):
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click inventory item (Salve graveyard teleport, Break)")

    # 5
    for i in range(3):
        if camera(pitch=319, yaw=1954, zoom=339, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 6
    for i in range(3):
        if click_tile(3427, 3461, action="Walk here", tile_radius=20, right_click=False):
            if wait_till_character_stopped_moving():
                    break
            if i == 2:
                exit("Failed to walk to (3427, 3461)")


def hop_if_players_nearby():
    hop_tile = (3440, 3480, 0)
    stand_tile = (3427, 3461, 0)

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
    walk_to_ghouls()
    hop_if_players_nearby()
    print("Navigation complete - ready for fighting.")

if __name__ == "__main__":
    run()
