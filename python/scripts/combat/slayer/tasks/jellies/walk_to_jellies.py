import time, re, random, math
from modules.banking.bank_castlewars import bank_castlewars
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.player_data.ensure_correct_attack_style import ensure_correct_combat_style
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
from modules.core.plugin_client import fetch_object
from modules.object_data.object import click_object
from modules.core.mouse_control import move
from modules.widgets.widget_data import get_all_widget_data
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.core.plugin_client import slayer_task_remaining
from modules.utils.check_if_in_tile import is_player_idle, check_if_in_tile
from modules.widgets.widget import get_widget, check_widget, check_widget_text, check_widget_name, click_widget, click_widget_child, click_widget_by_name
from modules.npc_data.click_npc import get_player_position, click_npc, click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_equipped_glory, click_lowest_games_necklace
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.utils.click_tile import click_tile

from modules.utils.hop import hop_to_random_world
from modules.banking.bank_castlewars import bank_castlewars
from modules.utils.check_players import check_for_players
from scripts.combat.slayer.slayer_gear import get_target_gear


def go_to_bank():
    """Go to bank and get target gear and inventory."""
    target_gear = get_target_gear()

    target_inventory = {
    "Amulet of glory": 1,
    "Games necklace": 1,
    "Prayer potion": 8,
    "Ring of dueling": 2,
    "Coins": 20,
    }

    bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)
    ensure_correct_combat_style()

def walk_to_jellies():
    """Walk to the jellies location."""
    # 1 ANKOU
    for i in range(5):
        if click_lowest_games_necklace(action='rub'):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click lowest games necklace")

    # 2
    for i in range(5):
        if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=5, right_click=False, action=None):   
            wait_for_tile_change()
            break
        if i == 4:
            exit("Failed to click dialogue option (wintertodt camp.) via child")
        wait_for_next_tick()

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
            wait_till_character_stopped_moving()
            wait_for_next_tick()
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (minecart, travel)")

    # 6
    for i in range(5):
        if click_widget_child('62062601', sprite_id=None, hidden=False, child_index=4, right_click=False, action=None):
            wait_for_tile_change()
            wait_for_next_tick(num_ticks=2)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")
    # 7
    for i in range(5):
        if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click dialogue option (look north) via child")


    # 8
    if not click_minimap_tile(1666, 3672, rand_x=2, rand_y=2, target_zoom=2.0):
        print("Failed to click minimap tile (1666, 3672)")
        exit()
    else:
        wait_till_character_stopped_moving(required_idle_ticks=2)

    for i in range(10):
        if click_minimap_tile(1655, 3673, rand_x=1, rand_y=1, target_zoom=2.0):
            print("clicked minimap tile (3303, 3125)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (3303, 3125)")


    # 10
    if not click_minimap_tile(1636, 3673, rand_x=1, rand_y=1, target_zoom=2.0):
        print("Failed to click minimap tile (1636, 3673)")
        exit()
    else:
        wait_till_character_stopped_moving()
        wait_for_next_tick(3)

    # 11
    for i in range(5):
        if click_gameobject("27785", 'investigate', tile=(1637, 3673), radius=20):
            wait_till_character_stopped_moving()
            wait_for_tile_change()
            wait_for_tick(3)
            break
        wait_for_next_tick()
        if i == 4:
            exit("Failed to click object (statue, investigate)")


    # 1
    for i in range(10):
        if click_minimap_tile(1690, 10033, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1690, 10033)")
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1690, 10033)")

    # 5
    for i in range(10):
        if click_minimap_tile(1716, 10045, rand_x=2, rand_y=2, target_zoom=2.0):
            print("clicked minimap tile (1716, 10045)")
            toggle_prayer('PROTECT_FROM_MELEE', activate=True)
            if wait_till_character_stopped_moving(required_idle_ticks=2):
                break
        wait_for_next_tick()
        if i == 9:
            exit("Failed to click minimap tile (1716, 10045)")


def hop_if_players_nearby():
    """Hop worlds if players are detected nearby."""
    hop_tile =  (1716, 10045, 0)
    stand_tile =  (1716, 10045, 0)

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
    walk_to_jellies()
    hop_if_players_nearby()


if __name__ == "__main__":
    run()
