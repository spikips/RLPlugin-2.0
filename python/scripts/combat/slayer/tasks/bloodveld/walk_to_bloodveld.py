import time
from modules.object_data.game_object import click_gameobject
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_equipped_ring_of_wealth, click_lowest_games_necklace
from modules.utils.camera import camera
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.click_tile import click_tile
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.widgets.widget import click_widget, click_widget_child


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear

def go_to_bank():
    target_gear = get_target_gear()

    target_inventory = {
        "Prayer potion": 6,
        "Amulet of glory": 1,
        "Ring of dueling": 2,
        "Cannon barrels": 1,
        "Cannon furnace": 1,
        "Cannon base": 1,
        "Cannon stand": 1,
        "Steel cannonball": "all"
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)

def walk_to_bloodveld():
    for i in range(5):
        if click_equipped_ring_of_wealth(action='Grand Exchange'):
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click jewelry: Ring of wealth (5) (Grand Exchange)")

    # 2
    # parent id: 35913752
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")

    # 3
    for i in range(10):
        if click_minimap_tile(3184, 3508, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3184, 3508)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                wait_for_next_tick(2)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3184, 3508)")

    # 4
    # Object click: spirit tree -> Travel
    for i in range(5):
        if click_gameobject("1295", 'Travel', tile=(3184, 3509), radius=20):
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (spirit tree, Travel)")

    # 5
    # parent id: 62062601
    for i in range(5):
        if click_widget_child('62062601', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
            if wait_for_tile_change():
                wait_for_next_tick(2)
                break
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (<col=ffffff>2</col>: gnome stronghold) via child")

    # 6
    for i in range(10):
        if click_minimap_tile(2435, 3425, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2435, 3425)")
            # 7
            for i in range(3):
                if camera(pitch=453, yaw=14, zoom=423, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2435, 3425)")



    # 8
    # Object click: cave -> Enter
    for i in range(5):
        if click_gameobject("26709", 'Enter', tile=(2428, 3424), radius=20):
            wait_till_character_stopped_moving(required_idle_ticks=2)
            wait_for_tile_change()
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (cave, Enter)")

    # 9
    for i in range(10):
        if click_minimap_tile(2463, 9822, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2463, 9822)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2463, 9822)")

    # 10
    for i in range(10):
        if click_minimap_tile(2476, 9816, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (2476, 9816)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (2476, 9816)")

    # 11
    for i in range(3):
        if click_tile(2479, 9819, action="Walk here", tile_radius=20, right_click=False):
            if wait_till_character_stopped_moving():
                    break
            if i == 2:
                exit("Failed to walk to (2479, 9819)")

def hop_if_players_nearby():
    hop_tile =  (2479, 9818, 0)
    stand_tile =  (2495, 9819, 0)

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
    walk_to_bloodveld()
    hop_if_players_nearby()
    print("Navigation complete - ready for fighting.")

if __name__ == "__main__":
    run()