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



# 1
for i in range(5):
    if click_equipped_glory(action='Al Kharid'):
        wait_for_tile_change()
        wait_for_next_tick()
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click equipped amulet of glory (Al Kharid)")

# 2
for i in range(2):
    if click_object("1511", 'open', tile=(3292, 3167), radius=20):
        wait_till_character_stopped_moving()
        break
    wait_for_next_tick()

# 3
for i in range(5):
    if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click dialogue option (look north) via child")

# 4
for i in range(3):
    if camera(pitch=319, yaw=0, zoom=306, speed=10):
        break
    if i == 2:
        exit("Failed to set camera")

# 5
if not click_minimap_tile(3276, 3148, rand_x=2, rand_y=2, target_zoom=2.0):
    print("Failed to click minimap tile (3276, 3148)")
    exit()
else:
    wait_till_character_stopped_moving()

# 6
for i in range(3):
    if camera(pitch=289, yaw=930, zoom=265, speed=10):
        wait_for_next_tick(2)
        break
    if i == 2:
        exit("Failed to set camera")

# 7
for i in range(5):
    if click_gameobject("41311", 'board', tile=(3270, 3143), radius=20):
        wait_for_tile_change()
        wait_for_next_tick(10)
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click object (ferry, board)")

# 8
for i in range(10):
    if click_minimap_tile(3180, 2841, rand_x=2, rand_y=2, target_zoom=2.0):
        print("clicked minimap tile (3180, 2841)")
        wait_till_character_stopped_moving()
        break
    wait_for_next_tick()
    if i == 9:
        exit("Failed to click minimap tile (3180, 2841)")

# 9
for i in range(3):
    if camera(pitch=295, yaw=1593, zoom=230, speed=10):
        break
    if i == 2:
        exit("Failed to set camera")

# 10
for i in range(10):
    if not click_closest_npc('shantay guard', option='buy-pass', max_attempts=5):
        wait_for_next_tick()
    else:
        if wait_till_character_stopped_moving():
            break
    if i == 9:
        exit("Failed to click npc (shantay guard)")

# 11
for i in range(5):
    if click_gameobject("41326", 'go-through', tile=(3194, 2841), radius=20):
        wait_till_character_stopped_moving()
        wait_for_next_tick(2)
        break
    wait_for_next_tick()
    if i == 4:
        exit("Failed to click object (shantay pass, go-through)")

# 12
if not click_minimap_tile(3194, 2828, rand_x=2, rand_y=2, target_zoom=2.0):
    print("Failed to click minimap tile (3194, 2828)")
    exit()
else:
    wait_till_character_stopped_moving()
