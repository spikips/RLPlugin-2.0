import time, re, random, math
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.utils.wait_for_tick import wait_for_tick, wait_for_next_tick
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.inventory import check_inventory, get_inventory_count, click_inventory_sequence
from modules.widgets.widget import check_widget_text, click_widget, check_widget_name, check_widget, get_widget, click_widget_child, click_widget_by_name
from modules.core.plugin_client import tile, stats
from modules.weapon_data.combat_style import combat_style
from modules.utils.camera import camera
from modules.utils.select_menu_option import select_menu_option
from modules.player_data.click_equipment import click_equipment_item
from modules.utils.inventory import click_inventory
from modules.object_data.game_object import click_gameobject, get_closest_game_object
from modules.object_data.object import click_object
from modules.widgets.widget import click_widget_child
from modules.npc_data.click_npc import click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_equipped_glory

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
    "Coins": 1000,
    "antidote++": 1
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)


def walk_to_kalphites():
    """Walk to the kalphites location."""
        # 2
    # Clicked jewelry: Amulet of glory(6) (action: Al Kharid) - Equipment tab open -> using equipped
    for i in range(5):
        if click_equipped_glory(action='Al Kharid'):
            wait_for_tile_change()
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click jewelry: Amulet of glory(6) (Al Kharid)")

    for i in range(3):
        if camera(pitch=268, yaw=1052, zoom=107, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 4
    # Object click: large door -> Open
    break_out_of_loop = False
    for x in range(5):
        for i in range(2):
            if click_object("1511", 'open', tile=(3292, 3167), radius=20):
                wait_till_character_stopped_moving(required_idle_ticks=2)
                break
            wait_for_next_tick()


            if click_minimap_tile(3303, 3134, rand_x=2, rand_y=2, target_zoom=2.0):
                print("clicked minimap tile (3303, 3134)")
                if wait_till_character_stopped_moving():
                    break_out_of_loop = True
                    break
            wait_for_next_tick()

        if break_out_of_loop:
            break

        if x == 4:
            exit("Failed to click minimap tile (3303, 3134)")

    # 7
    for i in range(10):
        if click_minimap_tile(3303, 3125, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3303, 3125)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3303, 3125)")

    # 8
    for i in range(3):
        if camera(pitch=512, yaw=1351, zoom=289, speed=10):
            break
        if i == 2:
            exit("Failed to set camera")

    # 9
    # {'npc_name': 'Shantay', 'npc_tile': {'plane': 0, 'y': 3121, 'x': 3307}, 'canvas_pos': {'y': 130, 'x': 157}, 'entity_type': 'npc', 'npc_id': 22805, 'tick': 2386, 'clicked_tile': {'plane': 0, 'x': 3307, 'y': 3120}, 'type': 'menu_option', 'option': 'Buy-pass', 'target': 'Shantay', 'npc_index': 0}
    for i in range(10):
        if not click_closest_npc('shantay', option='buy-pass', max_attempts=5, exact_name=True):
            wait_till_character_stopped_moving(required_idle_ticks=2)
        else:
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        if i == 9:
            exit("Failed to click npc (shantay)")

    # 11
    # for i in range(15):
    #     if click_widget_child('37027857', hidden=None, child_index=17):
    #         wait_till_character_stopped_moving()
    #         wait_for_next_tick(2)
    #         break
    #     wait_for_next_tick()
    # 11
    for i in range(5):
        if click_gameobject("4031", 'Go-through', radius=20):
            wait_till_character_stopped_moving()
            for _ in range(5):
                click_widget('37027860')
                if click_widget('37027857'):
                    break
                wait_for_next_tick(1)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (shantay pass, go-through)")

    wait_for_next_tick(3)

    for i in range(5):
        if click_gameobject("41326", 'go-through', tile=(3194, 2841), radius=20):
            wait_till_character_stopped_moving()
            wait_for_next_tick(2)
            for _ in range(5):
                if click_widget('37027860'):
                    if click_widget('37027857'):
                        break
                wait_for_next_tick(1)

    # 12
    for i in range(10):
        if click_minimap_tile(3321, 3124, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3321, 3124)")
            for i in range(3):
                if camera(pitch=306, yaw=1369, zoom=356, speed=10):
                    break
                if i == 2:
                    exit("Failed to set camera")
            if wait_till_character_stopped_moving():
                wait_for_next_tick(2)
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3321, 3124)")

    # 16
    # Object click: cave -> Enter
    for i in range(5):
        if click_gameobject("30180", 'Enter', tile=(3320, 3122), radius=20):
            wait_until_at_tile(3305, 9497)
            wait_for_next_tick(2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (cave, Enter)")

    # 17
    if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    # 18
    for i in range(5):
        if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to activate prayer (protect from melee)")

    # 19
    if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

    # 20
    for i in range(10):
        if click_minimap_tile(3319, 9481, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (3319, 9481)")
            if wait_till_character_stopped_moving():
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3319, 9481)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
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
    """Execute the main sequence: go to bank, walk to location, and check for players."""
    go_to_bank()
    walk_to_kalphites()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
