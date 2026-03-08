
import time
from modules.object_data.game_object import click_gameobject
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_lowest_games_necklace
from modules.utils.camera import camera
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.utils.wait_for_tick import wait_for_next_tick, wait_for_tick
from modules.widgets.widget import click_widget, click_widget_child


from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Prayer potion": 4,
    "Games necklace": 1,
    "Amulet of glory": 1,
    "Ring of dueling": 2,
    "Cannon barrels": 1,
    "Cannon furnace": 1,
    "Cannon base": 1,
    "Cannon stand": 1,
    "Steel cannonball": "all",
    "Coins": 20
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


def walk_to_moss_giants():
    """Walk to the moss_giants location."""
    for i in range(5):
        if click_lowest_games_necklace(action='rub'):
            wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click lowest games necklace")

    # 2
    for i in range(5):
        if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=5, right_click=False, action=None):   
            wait_for_tile_change()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (wintertodt camp.) via child")

    # 3
    if not click_minimap_tile(1645, 3929, rand_x=2, rand_y=2, target_zoom=2.0):
        print("Failed to click minimap tile (1645, 3929)")
        exit()
    else:
        wait_till_character_stopped_moving(required_idle_ticks=2)

    # 4
    for i in range(3):
        if camera(pitch=372, yaw=1735, zoom=287, speed=10):
            wait_for_next_tick(2)
            break
        if i == 2:
            exit("Failed to set camera")

    # 5
    for i in range(5):
        if click_gameobject("28835", 'travel', radius=20):
            wait_till_character_stopped_moving(required_idle_ticks=2)
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (minecart, travel)")

    #6
    for i in range(5):
        if click_widget_child('62062601', sprite_id=None, hidden=False, child_index=11, right_click=False, action=None):
            wait_for_tile_change()
            wait_for_next_tick(num_ticks=2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click 62062601")


    1
    for i in range(3):
        if camera(pitch=372, yaw=1734, zoom=226, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 2
    for i in range(5):
        if click_gameobject("42248", 'enter', tile=(1422, 3589), radius=20):
            if wait_until_at_tile(1432, 9913):
                print('entered giants den')
            else:
                exit('failed to enter giants den')

            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (cave, enter)")

    # 1
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")

    # 3
    if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    # 4
    for i in range(5):
        if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to activate prayer (protect from melee)")

    # 5
    if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    # 6
    for i in range(10):
        if click_minimap_tile(1431, 9877, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1431, 9877)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1431, 9877)")

    # 7
    for i in range(10):
        if click_minimap_tile(1424, 9864, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1424, 9864)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1424, 9864)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile =  (1414, 9865, 0)
    stand_tile =  (1419, 9862, 0)

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
    """Execute the main sequence: go to bank, walk to location, and check for players."""
    go_to_bank()
    walk_to_moss_giants()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
