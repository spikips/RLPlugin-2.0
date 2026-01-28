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


# 1 ANKOU
for i in range(5):
    if click_lowest_games_necklace(action='rub'):
        wait_for_next_tick(2)
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

# 3
if not click_minimap_tile(1645, 3929, rand_x=2, rand_y=2, target_zoom=2.0):
    print("Failed to click minimap tile (1645, 3929)")
    exit()
else:
    wait_till_character_stopped_moving()

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
    wait_till_character_stopped_moving()

# 9
if not click_minimap_tile(1655, 3673, rand_x=1, rand_y=1, target_zoom=2.0):
    print("Failed to click minimap tile (1655, 3673)")
    exit()
else:
    wait_till_character_stopped_moving()

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

# 12
if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
   exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# 13
for i in range(5):
    if click_widget('35454999', action="activate", hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to toggle prayer (protect from melee)")

# 14
if not click_minimap_tile(1654, 10024, rand_x=2, rand_y=2, target_zoom=2.0):
    print("Failed to click minimap tile (1654, 10024)")
    exit()
else:
    wait_till_character_stopped_moving()

# 15
if not click_minimap_tile(1646, 10009, rand_x=1, rand_y=1, target_zoom=3.0):
    print("Failed to click minimap tile (1646, 10009)")
    exit()
else:
    wait_till_character_stopped_moving()

# 16
for i in range(5):
    if click_gameobject("28892", 'squeeze-through', tile=(1648, 10008), radius=20):
        wait_until_at_tile(1646, 10000, radius=1, plane=0, timeout_seconds=10)
        wait_for_next_tick()
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click object (crack, squeeze-through)")

# 17
for i in range(3):
    if click_tile(1643, 9995, plane=0, action="Walk here", tile_radius=2, right_click=False):
       if wait_till_character_stopped_moving():
            break
    if i == 2:
        exit("Failed to walk to (1643, 9995)")
