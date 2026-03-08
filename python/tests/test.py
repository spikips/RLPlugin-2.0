import time, re, random, math

import keyboard
from modules.core.plugin_client import inventory, bank_items, cannon_data, minimap_tile_point, npc_agro, player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.player_data.cannon import click_cannon
from modules.utils.check_if_in_area import check_if_in_area
from modules.utils.check_players import check_for_players
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change, wait_until_at_tile
from modules.utils.hop import hop_to_random_world
from modules.utils.loot import has_ground_items, loot_all_ground_items
from modules.utils.wait_for_tick import wait_for_tick, wait_for_next_tick
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.inventory import check_inventory, get_inventory_count, click_inventory_sequence
from modules.widgets.widget import check_widget_text, click_widget, check_widget_name, check_widget, get_widget, click_widget_child, click_widget_by_name
from modules.core.plugin_client import tile, stats
from modules.weapon_data.combat_style import combat_style
from modules.utils.camera import camera
from modules.utils.select_menu_option import select_menu_option
from modules.player_data.click_equipment import click_equipment_item
from modules.utils.inventory import click_inventory, is_inventory_full
from modules.object_data.game_object import click_gameobject, get_closest_game_object
from modules.core.plugin_client import fetch_object
from modules.object_data.object import click_object, get_closest_object
from modules.core.mouse_control import move, right_click
from modules.widgets.widget_data import get_all_widget_data
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.core.plugin_client import slayer_task_remaining
from modules.utils.check_if_in_tile import is_player_idle, check_if_in_tile
from modules.widgets.widget import get_widget, check_widget, check_widget_text, check_widget_name, click_widget, click_widget_child, click_widget_by_name
from modules.npc_data.click_npc import get_player_position, click_npc, click_closest_npc
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
from modules.utils.automatic_scripting.small_functions import click_equipped_glory, click_equipped_necklace_of_passage, click_equipped_ring_of_wealth, click_lowest_games_necklace, click_lowest_glory, click_lowest_necklace_of_passage, click_lowest_ring_of_dueling
from modules.player_data.prayer.toggle_prayer import toggle_prayer
from modules.utils.click_tile import click_tile
from modules.player_data.check_run import click_run
from modules.banking.bank_castlewars import bank_castlewars, clean_item_name, get_inventory_data

print(check_widget_text(15138822))




# Inventory item click: Uncut sapphire -> Cut


# 1
# Inventory item click: Needle -> Use
# for i in range(5):
#     if click_inventory('needle', action='use', hover_only=False):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Needle, Use)")

# # 2
# # Inventory item click: Needle -> Leather -> Use
# for i in range(5):
#     if click_inventory('leather', action='use', hover_only=False):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Needle -> Leather, Use)")

# for i in range(5):
#     if click_widget_by_name('leather gloves', action='make', canvas=(0, 341, 514, 141)):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Leather gloves, Make)")

# for i in range(5):
#     if click_widget_child('30474246', sprite_id=None, hidden=None, child_index=0, right_click=False, action="collect to bank"):
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (collect to bank) via child")


# check_widget('30474242', sprite_id=None, hidden=None, child_index=11)
# 1
# for i in range(10):
#     if not click_closest_npc('grand exchange clerk', option='exchange', max_attempts=5):
#         wait_for_next_tick()
#     else:
#         if wait_till_character_stopped_moving():
#             break
#     if i == 9:
#         exit("Failed to click npc (grand exchange clerk)")


# for i in range(5):
#     if click_widget_child('30474247', sprite_id=None, hidden=None, child_index=3, right_click=False, action=None):
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (create <col=ff9040>buy</col> offer) via child")

# click_widget_by_name('ring of wealth (5)', action='Select')

# parent id: 30474266
# for i in range(4):
#     click_widget_child('30474266', sprite_id=None, hidden=None, child_index=13, right_click=False, action=None)


# for i in range(5):
#     if click_widget_child('30474270', sprite_id=None, hidden=None, child_index=3, right_click=False, action=None):
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (confirm) via child")


# for i in range(5):
#     if click_widget_child('30474246', sprite_id=None, hidden=None, child_index=0, right_click=False, action=None):
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (collect to inventory) via child")



# 1
# parent id: 30474248
# for i in range(5):
#     if click_widget_child('30474248', sprite_id=None, hidden=None, child_index=2, right_click=False, action="abort offer"):
#         wait_for_tick(2)
#         for i in range(5):
#             if click_widget_child('30474246', sprite_id=None, hidden=None, child_index=0, right_click=False, action=None):
#                 break
#             wait_for_next_tick()
#             if i == 4:
#                 exit("Failed to click dialogue option (collect to inventory) via child")
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (modify offer) via child")














# def auto_retaliate(enable: bool):
#     # open combat options tab
#     if not click_widget('35913792', sprite_id=1026, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#         exit(f'click widget 35913792 failed, exiting... time: {time.strftime("%H:%M:%S")}')

#     if enable:
#         check_auto_retaliate = check_widget("38862882", sprite_id=1141)
#         if check_auto_retaliate:
#             for i in range(5):
#                     if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
#                         print('enabled auto retaliate')
#                         break
#                     wait_for_next_tick()
#                     if i == 4:
#                         exit("Failed to click dialogue option (auto retaliate) via child")
#     else:
#         check_auto_retaliate = check_widget("38862882", sprite_id=1150)
#         if check_auto_retaliate:
#             for i in range(5):
#                     if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
#                         print('disabled auto retaliate')
#                         break
#                     wait_for_next_tick()
#                     if i == 4:
#                         exit("Failed to click dialogue option (auto retaliate) via child")
#     # open inventory
#     if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#         exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # auto_retaliate(enable=False)
# # auto_retaliate(enable=True)

# 2
# parent id: 38862848
# for i in range(5):
#     if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (auto retaliate) via child")

# # 3
# # parent id: 38862848
# for i in range(5):
#     if click_widget_child('38862880', sprite_id=None, hidden=None, child_index=8, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (auto retaliate) via child")

# 4
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')






# def get_widget_item_quantities(item_names: list[str]) -> dict[str, int]:
#     """
#     Return quantities for each item in `item_names` by parsing the current
#     inventory widget data (falls back to plugin inventory()). Names are
#     normalized using `clean_item_name` so matching is case-insensitive and
#     ignores trailing charge/dose suffixes like "(3)".

#     Returns a dict mapping the original requested name to the aggregated
#     quantity found (0 if not present).
#     """
#     if not item_names:
#         return {}

#     # Map normalized base -> original provided name (first occurrence)
#     normalized_to_original: dict[str, str] = {}
#     for orig in item_names:
#         normalized_to_original[clean_item_name(orig)] = orig

#     # Prepare result with 0 defaults
#     results: dict[str, int] = {orig: 0 for orig in item_names}

#     inv = get_inventory_data()
#     if not inv:
#         return results

#     for entry in inv:
#         raw_name = entry.get('name', '')
#         if not raw_name:
#             continue
#         base = clean_item_name(raw_name)
#         qty = int(entry.get('quantity', 1) or 0)

#         if base in normalized_to_original:
#             orig = normalized_to_original[base]
#             results[orig] += qty

#     return results

# print(get_widget_item_quantities(['adamant 2h sword', 'adamant battleaxe', 'rune scimitar', 'fire rune', 'nature rune', 'death rune']))


# click_widget_by_name('High Level Alchemy', action='Cast')

# for i in range(5):
#     if click_object("30236", 'Enter', tile=(1436, 3671), radius=20):
#         wait_till_character_stopped_moving(required_idle_ticks=2)
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (chasm, Enter)")

# 1
# Clicked jewelry: Ring of wealth (5) (action: Grand Exchange) - Equipment tab open -> using equipped
# for i in range(5):
#     if click_equipped_ring_of_wealth(action='Grand Exchange'):
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Ring of wealth (5) (Grand Exchange)")

# # 2
# # parent id: 35913752
# for i in range(5):
#     if click_widget_child('35913752', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")

# # 3
# for i in range(10):
#     if click_minimap_tile(3184, 3508, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3184, 3508)")
#         if wait_till_character_stopped_moving():
#             wait_for_next_tick(2)
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3184, 3508)")

# # 4
# # Object click: spirit tree -> Travel
# for i in range(5):
#     if click_gameobject("1295", 'Travel', tile=(3184, 3509), radius=20):
#         if wait_till_character_stopped_moving(required_idle_ticks=2):
#             break
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (spirit tree, Travel)")

# # 5
# # parent id: 62062601
# for i in range(5):
#     if click_widget_child('62062601', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
#         if wait_till_character_stopped_moving(required_idle_ticks=2):
#             break
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (<col=ffffff>2</col>: gnome stronghold) via child")

# # 6
# for i in range(10):
#     if click_minimap_tile(2435, 3425, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2435, 3425)")
#         # 7
#         for i in range(3):
#             if camera(pitch=453, yaw=14, zoom=423, speed=10):
#                 break
#             if i == 2:
#                 exit("Failed to set camera")
#         if wait_till_character_stopped_moving(required_idle_ticks=2):
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2435, 3425)")



# # 8
# # Object click: cave -> Enter
# for i in range(5):
#     if click_gameobject("26709", 'Enter', tile=(2428, 3424), radius=20):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (cave, Enter)")

# # 9
# for i in range(10):
#     if click_minimap_tile(2463, 9822, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2463, 9822)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2463, 9822)")

# # 10
# for i in range(10):
#     if click_minimap_tile(2476, 9816, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2476, 9816)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2476, 9816)")

# # 11
# for i in range(3):
#     if click_tile(2479, 9819, action="Walk here", tile_radius=20, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (2479, 9819)")

        


# # RARE_ITEMS = ['Mystic hat (dark)', 'Mystic boots (dark)']
# # COMMON_ITEMS = ['Death rune']  # Or add more commons if desired
# # def loot_drops():
# #     """Loot drops similar to ogre.py style.
# #     - Triggers special phase only on rares.
# #     - Always loots commons if rares are present.
# #     - Returns True if any looting occurred."""
    
# #     looted = False
    
# #     # Check for rares only (one efficient call if function accepts list)
    
# #     if has_ground_items(RARE_ITEMS, tile_radius=20):
# #         print("Rare drop(s) detected - entering loot phase")
        
# #         # Loot all rares
# #         for item in RARE_ITEMS:
# #             if loot_all_ground_items(item):
# #                 looted = True
        
# #         # Loot commons while we're here (extra death runes during rare phase)
# #         for item in COMMON_ITEMS:
# #             if loot_all_ground_items(item):
# #                 looted = True

# #     else:
# #         # Optional quick common looting even without rares (safe during combat)
# #         for item in COMMON_ITEMS:
# #             if loot_all_ground_items(item):
# #                 looted = True
    
# #     return looted


# # start_time = time.perf_counter()
# # loot_drops()
# # end_time = time.perf_counter()

# # elapsed = end_time - start_time
# # print(f"Function took {elapsed:.4f} seconds")


# # toggle_prayer('PROTECT_FROM_MAGIC', activate=True)

# # Object click: broken window -> Climb-through


# # for index in range(0, 28):
# # for i in range(5):
# #     if click_lowest_glory(action='Rub'):
# #         break
# #     wait_for_next_tick()
# #     if i == 4:
# #         exit("Failed to click jewelry: Amulet of glory(5) (Rub)")

# # # 2
# # # parent id: 14352385
# # for i in range(5):
# #     if click_widget_child('14352385', sprite_id=None, hidden=None, child_index=1, right_click=False, action=None):
# #         break
# #     wait_for_next_tick()
# #     if i == 4:
# #         exit("Failed to click dialogue option (edgeville) via child")

# #{'random_clickpoint': {'x': 704, 'y': 272}, 'itemId': 995, 'quantity': 7626, 'spriteId': -1, 'name': '<col=ff9040>Coins</col>', 'bounds': {'x': 696, 'width': 36, 'y': 249, 'height': 32}, 'id': 983043, 'text': '', 'OnOpListener': [487, -2147483645, -2147483643, 100, 0], 'textColor': 0, 'hasOnOpListener': True, 'enabled': False}


# # print(check_for_players(max_wait_ticks=1))

# # target_gear = [
# #     "Amulet of glory",
# #     "Ancient cloak",
# #     "Ancient mitre",
# #     "Antler guard",
# #     "Brine sabre",
# #     "Climbing boots",
# #     "Combat bracelet",
# #     "Honourable blessing",
# #     "Monk's robe",
# #     "Monk's robe top",
# #     "Ring of wealth"
# # ]

# # target_inventory = {
# #     "Amulet of glory": 1,
# #     "Games necklace": 1,
# #     "Prayer potion": 5,
# #     "Ring of dueling": 2,
# # }

# # bank_castlewars(target_gear=target_gear, target_inventory=target_inventory)

# # for i in range(3):
# #     if camera(pitch=434, yaw=1710, zoom=352, speed=10):
# #         break
# #     if i == 2:
# #         exit("Failed to set camera")

# # for i in range(5):
# #     if click_gameobject("4483", 'Use', tile=(2444, 3083), radius=20):
# #         wait_till_character_stopped_moving()
# #         wait_for_next_tick(1)
# #         break
# #     wait_for_next_tick()
# #     if i == 4:
# #         exit("Failed to click object (bank chest, Use)")

# print(check_inventory("slayer helmet"))
# # print(f"gear: {gear()}\n\ninventory: {inventory()}")






# def get_slayer_monster_name(widget_id=15138822):
#     """
#     Extracts and returns only the monster name from the slayer task widget text.
#     Example input:  "Your new task is to kill 27 Ankou."
#     Example output: "Ankou"
    
#     Handles multi-word names like "Cave horrors" → "Cave horrors"
#     Removes the trailing period and any extra whitespace.
#     Returns None if no text or no match.
#     """
#     text = check_widget_text(widget_id)
    
#     if not text:
#         print("No text found in widget")
#         return None
    
#     # Optional: print the raw text for debugging
#     # print(f"Raw task text: {text}")
    
#     # Regex pattern: captures everything after the number until the final period
#     match = re.search(r'to kill \d+\s+(.+?)\.', text.strip())
    
#     if match:
#         monster_name = match.group(1).strip()
#         print("Task assigned:", monster_name)
#         return True
#     else:
#         print(f"Could not parse monster name from text: {text}")
#         return None
# time.sleep(3)
# get_slayer_monster_name()
# 1
# Inventory item click: Fenkenstrain's castle teleport -> Break
# for i in range(5):
    # if click_inventory("fenkenstrain's castle teleport", action='break', hover_only=False):
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Fenkenstrain's castle teleport, Break)")

# # 2
# for i in range(10):
#     if click_minimap_tile(3558, 3504, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3558, 3504)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3558, 3504)")

# # 6
# for i in range(10):
#     if click_minimap_tile(3577, 3479, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3577, 3479)")
#         # parent id: 35913791
#         for i in range(5):
#             if click_widget_child('35913797', sprite_id=None, hidden=None, child_index=5, right_click=False, action=None):
#                 break
#             wait_for_next_tick()
#             if i == 4:
#                 exit("Failed to click dialogue option (prayer) via child")

#         # 4
#         for i in range(5):
#             if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#                 break
#             wait_for_next_tick()
#             if i == 4:
#                 exit("Failed to activate prayer (protect from melee)")

#         # 5
#         # parent id: 35913791
#         for i in range(5):
#             if click_widget_child('35913795', sprite_id=None, hidden=None, child_index=3, right_click=False, action=None):
#                 break
#             wait_for_next_tick()
#             if i == 4:
#                 exit("Failed to click dialogue option (inventory) via child")

#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3577, 3479)")

# # 7
# for i in range(10):
#     if click_minimap_tile(3592, 3480, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3592, 3480)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3592, 3480)")

# print(click_inventory("antidote++(3)"))

# # 2
# # Clicked jewelry: Amulet of glory(6) (action: Al Kharid) - Equipment tab open -> using equipped
# for i in range(5):
#     if click_equipped_glory(action='Al Kharid'):
#         wait_for_tile_change()
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Amulet of glory(6) (Al Kharid)")

# for i in range(3):
#     if camera(pitch=268, yaw=1052, zoom=107, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 4
# # Object click: large door -> Open
# for i in range(2):
#     if click_object("1511", 'open', tile=(3292, 3167), radius=20):
#         wait_till_character_stopped_moving()
#         break
#     wait_for_next_tick()


# # 6
# for i in range(10):
#     if click_minimap_tile(3303, 3134, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3303, 3134)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3303, 3134)")

# # 7
# for i in range(10):
#     if click_minimap_tile(3303, 3125, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3303, 3125)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3303, 3125)")

# # 8
# for i in range(3):
#     if camera(pitch=268, yaw=1052, zoom=356, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 9
# # {'npc_name': 'Shantay', 'npc_tile': {'plane': 0, 'y': 3121, 'x': 3307}, 'canvas_pos': {'y': 130, 'x': 157}, 'entity_type': 'npc', 'npc_id': 22805, 'tick': 2386, 'clicked_tile': {'plane': 0, 'x': 3307, 'y': 3120}, 'type': 'menu_option', 'option': 'Buy-pass', 'target': 'Shantay', 'npc_index': 0}
# for i in range(10):
#     if not click_closest_npc('shantay', option='buy-pass', max_attempts=5, exact_name=True):
#         wait_till_character_stopped_moving()
#     else:
#         if wait_till_character_stopped_moving():
#             break
#     if i == 9:
#         exit("Failed to click npc (shantay)")

# # 10
# # Object click: shantay pass -> Go-through
# for i in range(5):
#     if click_object("4031", 'Go-through', radius=20):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (shantay pass, Go-through)")

# # 11
# for i in range(5):
#     if click_widget_child('37027857', hidden=False, child_index=17):
#         wait_till_character_stopped_moving()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()

# # 12
# for i in range(10):
#     if click_minimap_tile(3321, 3124, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3321, 3124)")
#         for i in range(3):
#             if camera(pitch=306, yaw=1369, zoom=356, speed=10):
#                 break
#             if i == 2:
#                 exit("Failed to set camera")
#         if wait_till_character_stopped_moving():
#             wait_for_next_tick(2)
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3321, 3124)")

# # 16
# # Object click: cave -> Enter
# for i in range(5):
#     if click_gameobject("30180", 'Enter', tile=(3320, 3122), radius=20):
#         wait_for_tile_change()
#         wait_for_next_tick(1)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (cave, Enter)")

# # 17
# if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 18
# for i in range(5):
#     if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to activate prayer (protect from melee)")

# # 19
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 20
# for i in range(10):
#     if click_minimap_tile(3278, 9484, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3278, 9518)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3278, 9518)")


# 1
# Clicked jewelry: Ring of dueling(7) (action: Rub) - Inventory tab open -> using lowest charge
# for i in range(5):
    # if click_lowest_ring_of_dueling(action='Rub'):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Ring of dueling(7) (Rub)")

# # # 2
# for i in range(5):
#     if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=2, right_click=False, action=None):
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (castle wars arena.) via child")

# # 5
# for i in range(10):
#     if click_minimap_tile(2468, 3072, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2468, 3072)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2468, 3072)")

# # 6
# for i in range(10):
#     if click_minimap_tile(2488, 3086, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2488, 3086)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2488, 3086)")

# # 8
# for i in range(10):
#     if click_minimap_tile(2492, 3096, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2492, 3096)")
#         if wait_till_character_stopped_moving():
#             wait_for_tick(2)
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2492, 3096)")

# # 9
# for i in range(3):
#     if camera(pitch=330, yaw=0, zoom=573, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 11
# for i in range(3):
#     if click_tile(2494, 3098, action="Walk here", tile_radius=20, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (2494, 3098)")







# 1
# Inventory item click: Barrows teleport -> Break
# for i in range(5):
#     if click_inventory('barrows teleport', action='break', hover_only=False):
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Barrows teleport, Break)")

# # 3
# for i in range(3):
#     if camera(pitch=321, yaw=0, zoom=206, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 4
# for i in range(10):
#     if click_minimap_tile(3537, 3296, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3537, 3296)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3537, 3296)")

# # 6
# for i in range(10):
#     if click_minimap_tile(3522, 3279, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3522, 3279)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3522, 3279)")

# # 7
# for i in range(10):
#     if click_minimap_tile(3509, 3303, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3509, 3303)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3509, 3303)")

# # 8
# for i in range(3):
#     if click_tile(3506, 3312, action="Walk here", tile_radius=2, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (3506, 3312)")


# click_run(enable=True)
# 2
# Clicked jewelry: Amulet of glory(1) (action: Edgeville) - Equipment tab open -> using equipped
# for i in range(5):
#     if click_equipped_glory(action='Edgeville'):
#         wait_for_tile_change()
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Amulet of glory(1) (Edgeville)")

# # 3
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 4
# for i in range(5):
#     if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")

# # 6
# for i in range(10):
#     if click_minimap_tile(3082, 3474, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3082, 3474)")
#         if wait_till_character_stopped_moving():
#             wait_for_next_tick(2)
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3082, 3474)")


# # 1
# # Object click: soul wars portal -> Enter
# for i in range(5):
#     if click_gameobject("40474", 'Enter', tile=(3083, 3474), radius=20):
#         wait_for_tile_change()
#         wait_for_next_tick(3)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (soul wars portal, Enter)")

# # 2
# for i in range(10):
#     if click_minimap_tile(2210, 2825, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2210, 2825)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2210, 2825)")

# # 3
# for i in range(10):
#     if click_minimap_tile(2227, 2811, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2227, 2811)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2227, 2811)")

# # 4
# for i in range(10):
#     if click_minimap_tile(2245, 2831, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2245, 2831)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2245, 2831)")

# # 5
# for i in range(10):
#     if click_minimap_tile(2255, 2859, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2255, 2859)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2255, 2859)")

# # 6
# for i in range(10):
#     if click_minimap_tile(2277, 2866, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2277, 2866)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2277, 2866)")

# # 7
# for i in range(3):
#     if camera(pitch=324, yaw=0, zoom=207, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 8
# for i in range(10):
#     if click_minimap_tile(2298, 2873, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2298, 2873)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2298, 2873)")

# # 9
# for i in range(10):
#     if click_minimap_tile(2319, 2887, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2319, 2887)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2319, 2887)")

# # 10
# for i in range(10):
#     if click_minimap_tile(2324, 2910, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2324, 2910)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2324, 2910)")

# # 11
# for i in range(10):
#     if click_minimap_tile(2321, 2940, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2321, 2940)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2321, 2940)")

# # 12
# for i in range(10):
#     if click_minimap_tile(2319, 2956, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2319, 2956)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2319, 2956)")

# # 13
# for i in range(10):
#     if click_minimap_tile(2293, 2955, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2293, 2955)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2293, 2955)")

# # 14
# for i in range(10):
#     if click_minimap_tile(2278, 2963, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2278, 2963)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2278, 2963)")

# # 15
# for i in range(10):
#     if click_minimap_tile(2257, 2958, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2257, 2958)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2257, 2958)")














# 1
# if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 2
# for i in range(5):
#     if click_widget('35454999', action='activate', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to activate prayer (protect from melee)")

# # 3
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 4
# for i in range(5):
#     if click_inventory('salve graveyard teleport', action='break', hover_only=False):
#         wait_for_tile_change()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory item (Salve graveyard teleport, Break)")

# # 5
# for i in range(3):
#     if camera(pitch=319, yaw=1954, zoom=339, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 6
# for i in range(3):
#     if click_tile(3427, 3461, action="Walk here", tile_radius=2, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (3427, 3461)")





# 1
# Clicked jewelry: Amulet of glory(3) (action: Draynor Village) - Equipment tab open -> using equipped
# for i in range(5):
#     if click_equipped_glory(action='Draynor Village'):
#         wait_for_tile_change()
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Amulet of glory(3) (Draynor Village)")

# # 2
# for i in range(5):
#     if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")

# # 3
# for i in range(3):
#     if camera(pitch=341, yaw=0, zoom=380, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 4
# for i in range(10):
#     if click_minimap_tile(3071, 3259, rand_x=1, rand_y=1, target_zoom=2.0):
#         print("clicked minimap tile (3071, 3259)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3073, 3259)")


# # 6
# for i in range(10):
#     if click_minimap_tile(3057, 3245, rand_x=1, rand_y=1, target_zoom=2.0):
#         print("clicked minimap tile (3057, 3245)")
#         for i in range(3):
#             if camera(pitch=335, yaw=1196, zoom=352, speed=10):
#                 break
#             if i == 2:
#                 exit("Failed to set camera")
#         if wait_till_character_stopped_moving():
#             wait_for_next_tick(3)
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3054, 3245)")

# # 8
# for i in range(10):
#     if not click_closest_npc([8630], option='Port piscarilius', max_attempts=5):
#         wait_for_next_tick()
#     else:
#         if wait_until_at_tile(1824, 3695, plane=1):
#             wait_for_next_tick(6)
#             break
#     if i == 9:
#         exit("Failed to click npc (veos)")

# # 1
# for i in range(5):
#     if click_gameobject("27778", 'cross', tile=(1824, 3693), radius=20):
#         wait_till_character_stopped_moving()
#         wait_for_next_tick(3)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (gangplank, cross)")

# # 2
# for i in range(10):
#     if click_minimap_tile(1795, 3669, rand_x=1, rand_y=1, target_zoom=2.0):
#         print("clicked minimap tile (1795, 3669)")
#         for i in range(3):
#             if camera(pitch=266, yaw=1161, zoom=253, speed=10):
#                 break
#             if i == 2:
#                 exit("Failed to set camera")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1795, 3669)")



# # 1
# for i in range(10):
#     if click_minimap_tile(1795, 3646, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1795, 3646)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1795, 3646)")

# # 2
# for i in range(10):
#     if click_minimap_tile(1804, 3624, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1804, 3624)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1804, 3624)")

# # 3
# for i in range(10):
#     if click_minimap_tile(1812, 3606, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1812, 3606)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1812, 3606)")

# # 4
# for i in range(10):
#     if click_minimap_tile(1816, 3587, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1816, 3587)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1816, 3587)")

# # 5
# for i in range(10):
#     if click_minimap_tile(1838, 3579, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1838, 3579)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1838, 3579)")

# # 6
# for i in range(10):
#     if click_minimap_tile(1851, 3563, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1851, 3563)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1851, 3563)")

# # 7
# for i in range(10):
#     if click_minimap_tile(1859, 3553, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (1859, 3553)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (1859, 3553)")


# # 8
# for i in range(3):
#     if click_tile(1865, 3553, plane=0, action="Walk here", tile_radius=2, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (1865, 3553)")








# Clicked jewelry: Necklace of passage(1) (action: Rub) - Inventory tab open -> using lowest charge
# for i in range(5):
#     if click_lowest_necklace_of_passage(action='Rub'):
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click jewelry: Necklace of passage(1) (Rub)")

# # 2
# for i in range(5):
#     if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=2, right_click=False, action=None):
#         wait_for_tile_change()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (the outpost) via child")


# # 3
# for i in range(10):
#     if click_minimap_tile(2447, 3363, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (2447, 3363)")
#         if wait_till_character_stopped_moving():
#             break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (2447, 3363)")







# # 1 CROCODILE
# for i in range(5):
#     if click_equipped_glory(action='Al Kharid'):
#         wait_for_tile_change()
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click equipped amulet of glory (Al Kharid)")

# # 2
# for i in range(2):
#     if click_object("1511", 'open', tile=(3292, 3167), radius=20):
#         wait_till_character_stopped_moving()
#         break
#     wait_for_next_tick()

# # 3
# for i in range(5):
#     if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")

# # 4
# for i in range(3):
#     if camera(pitch=319, yaw=0, zoom=306, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 5
# if not click_minimap_tile(3276, 3148, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (3276, 3148)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 6
# for i in range(3):
#     if camera(pitch=289, yaw=930, zoom=265, speed=10):
#         wait_for_next_tick(2)
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 7
# for i in range(5):
#     if click_gameobject("41311", 'board', tile=(3270, 3143), radius=20):
#         wait_for_tile_change()
#         wait_for_next_tick(10)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (ferry, board)")

# # 8
# for i in range(10):
#     if click_minimap_tile(3180, 2841, rand_x=2, rand_y=2, target_zoom=2.0):
#         print("clicked minimap tile (3180, 2841)")
#         wait_till_character_stopped_moving()
#         break
#     wait_for_next_tick()
#     if i == 9:
#         exit("Failed to click minimap tile (3180, 2841)")

# # 9
# for i in range(3):
#     if camera(pitch=295, yaw=1593, zoom=230, speed=10):
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 10
# for i in range(10):
#     if not click_closest_npc('shantay guard', option='buy-pass', max_attempts=5):
#         wait_for_next_tick()
#     else:
#         if wait_till_character_stopped_moving():
#             break
#     if i == 9:
#         exit("Failed to click npc (shantay guard)")

# # 11
# for i in range(5):
#     if click_gameobject("41326", 'go-through', tile=(3194, 2841), radius=20):
#         wait_till_character_stopped_moving()
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (shantay pass, go-through)")

# # 12
# if not click_minimap_tile(3194, 2828, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (3194, 2828)")
#     exit()
# else:
#     wait_till_character_stopped_moving()



# # 1 ANKOU
# for i in range(5):
#     if click_lowest_games_necklace(action='rub'):
#         wait_for_next_tick(2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click lowest games necklace")

# # 2
# for i in range(5):
#     if click_widget_child('14352385', sprite_id=None, hidden=False, child_index=5, right_click=False, action=None):   
#         wait_for_tile_change()
#         break
#     if i == 4:
#         exit("Failed to click dialogue option (wintertodt camp.) via child")

# # 3
# if not click_minimap_tile(1645, 3929, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (1645, 3929)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 4
# for i in range(3):
#     if camera(pitch=372, yaw=1735, zoom=287, speed=10):
#         wait_for_next_tick(2)
#         break
#     if i == 2:
#         exit("Failed to set camera")

# # 5
# for i in range(5):
#     if click_gameobject("28835", 'travel', radius=20):
#         wait_till_character_stopped_moving()
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (minecart, travel)")

# # 6
# for i in range(5):
#     if click_widget_child('62062601', sprite_id=None, hidden=False, child_index=4, right_click=False, action=None):
#         wait_for_tile_change()
#         wait_for_next_tick(num_ticks=2)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")
# # 7
# for i in range(5):
#     if click_widget_child('35913752', sprite_id=None, hidden=False, child_index=1, right_click=False, action=None):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click dialogue option (look north) via child")


# # 8
# if not click_minimap_tile(1666, 3672, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (1666, 3672)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 9
# if not click_minimap_tile(1655, 3673, rand_x=1, rand_y=1, target_zoom=2.0):
#     print("Failed to click minimap tile (1655, 3673)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 10
# if not click_minimap_tile(1636, 3673, rand_x=1, rand_y=1, target_zoom=2.0):
#     print("Failed to click minimap tile (1636, 3673)")
#     exit()
# else:
#     wait_till_character_stopped_moving()
#     wait_for_next_tick(3)

# # 11
# for i in range(5):
#     if click_gameobject("27785", 'investigate', tile=(1637, 3673), radius=20):
#         wait_till_character_stopped_moving()
#         wait_for_tile_change()
#         wait_for_tick(3)
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (statue, investigate)")

# # 12
# if not click_widget('35913797', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913797 failed, exiting... time: {time.strftime("%H:%M:%S")}')

# # 13
# for i in range(5):
#     if click_widget('35454999', action="activate", hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to toggle prayer (protect from melee)")

# # 14
# if not click_minimap_tile(1654, 10024, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (1654, 10024)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 15
# if not click_minimap_tile(1646, 10009, rand_x=1, rand_y=1, target_zoom=3.0):
#     print("Failed to click minimap tile (1646, 10009)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# # 16
# for i in range(5):
#     if click_gameobject("28892", 'squeeze-through', tile=(1648, 10008), radius=20):
#         wait_until_at_tile(1646, 10000, radius=1, plane=0, timeout_seconds=10)
#         wait_for_next_tick()
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (crack, squeeze-through)")

# # 17
# for i in range(3):
#     if click_tile(1643, 9995, plane=0, action="Walk here", tile_radius=2, right_click=False):
#        if wait_till_character_stopped_moving():
#             break
#     if i == 2:
#         exit("Failed to walk to (1643, 9995)")



# # 1
# for i in range(5):
#     if click_inventory('cannon base', action='set-up', hover_only=False):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click inventory (cannon base)")





# for i in range(5):
#     if click_gameobject('reward cart', 'big-search', tile=(1638, 3946), radius=20):
#         break
#     wait_for_next_tick()
#     if i == 4:
#         exit("Failed to click object (reward cart, big-search)")



# if not click_widget('35913779', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913779 failed, exiting... time: {time.strftime("%H:%M:%S")}')


# if not click_minimap_tile(1639, 3943, rand_x=2, rand_y=2, target_zoom=2.0):
#     print("Failed to click minimap tile (1639, 3943)")
#     exit()
# else:
#     wait_till_character_stopped_moving()

# click_inventory('cannon base', action='Set-up', hover_only=False)

# click_object("29321", 'bank', tile=(1641, 3944), radius=20)

# click_object("55423", 'Big-search', tile=(1636, 3942), radius=20)

# click_closest_npc('captain kalt', option='check scores', max_attempts=5)

# on_tile = check_if_in_tile(x=1625, y=3938, plane=0, click=True, right_click=False)


# click_widget('35913796', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=1, rand_y=1, clicks=1, sleep_interval=(0, 0))
# click_widget('35913794', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=1, rand_y=1, clicks=1, sleep_interval=(0, 0))
# click_widget('35913793', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=1, rand_y=1, clicks=1, sleep_interval=(0, 0))
# click_widget('35913796', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=1, rand_y=1, clicks=1, sleep_interval=(0, 0))
# click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=1, rand_y=1, clicks=1, sleep_interval=(0, 0))


# remaining = slayer_task_remaining()
# print(f"Slayer task NPCs left: {remaining}")

# if remaining == 0:
#     print("Task complete - bank or get new task")
    
# vine_ids = ['13847', '13848', '13849']  # List of all possible vine IDs to try

# while get_inventory_count('short vine') < 3:
#     increased = False
#     for vine_id in vine_ids:
#         old_count = get_inventory_count('short vine')
#         click_vine = click_gameobject(vine_id, 'Cut-vine')
#         if not click_vine:
#             continue  # Try next vine ID if click failed
        
#         # Wait to see if count changed (with timeout to avoid infinite loop)
#         for _ in range(20):  # Adjust attempts as needed (e.g., 20 * 0.1s = 2s timeout)
#             time.sleep(0.1)
#             if get_inventory_count('short vine') > old_count:
#                 increased = True
#                 break
#         if increased:
#             break  # Successfully cut a vine, proceed to next one needed
#         # If not increased after timeout, try next ID
    
#     if not increased:
#         # No vine was cut after trying all, perhaps none available
#         print("No vines could be cut; stopping.")
#         break

# print(get_closest_game_object('13847', None, 10))

# print(npc(name='riyl shadow'))
# print(npc(name='nail beast'))
# print(npc(name='swamp snake'))
# print(npc(name='giant snail'))
# print(npc(name='vampyre juvinate'))
# print(npc(name='ghast'))

# def wait_till_character_stopped_moving(max_ticks=100):
#     """
#     Check if the player is idle (not moving) based on animation and tile stability.
#     Loops until the player is idle or max_ticks is reached.
    
#     Args:
#         max_ticks (int): Maximum number of ticks to wait before timing out (default: 100).
    
#     Returns:
#         True if the player becomes idle within max_ticks, False otherwise.
#     """
#     attempt = 0
#     while attempt < max_ticks:
#         pl_data = player(location=True, animation=True)
#         if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data'] or 'animation' not in pl_data['data']:
#             print("Failed to fetch player location or animation")
#             return False
        
#         initial_loc = pl_data['data']['location']
#         initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
        
#         wait_for_tick(ticks=1)
        
#         pl_data = player(location=True, animation=True)
#         if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
#             print("Failed to fetch player location after tick")
#             return False
        
#         current_loc = pl_data['data']['location']
#         current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
        
#         is_idle = current_tile == initial_tile and pl_data['data']['animation'] in [0, -1]
#         print(f"Player idle check (attempt {attempt + 1}): Tile unchanged: {current_tile == initial_tile}, Animation: {pl_data['data']['animation']}, Idle: {is_idle}")
        
#         if is_idle:
#             return True
        
#         attempt += 1
    
#     print(f"Timeout: Player did not become idle after {max_ticks} ticks")
#     return False

# wait_till_character_stopped_moving()


# print(stats()['data'])
# def get_magic_level_from_stats(stats_dict):
#     """Return the player's Magic level from the stats dict or None on failure."""
#     try:
#         return int(stats_dict['Magic']['level'])
#     except Exception as e:
#         print('Could not read Magic level from stats:', e)
#         return None


# def magic_spell_widget_for_level(level):
#     """Map a Magic level to the appropriate teleport widget ID.

#     Ranges (from repo comments):
#     - 25-30 -> '14286871'
#     - 31-36 -> '14286874'
#     - 37-44 -> '14286877'
#     - 45+   -> '14286882'
#     Returns the widget id string or None if no mapping.
#     """
#     if level is None:
#         return None
#     if 25 <= level <= 30:
#         return '14286871'
#     if 31 <= level <= 36:
#         return '14286874'
#     if 37 <= level <= 44:
#         return '14286877'
#     if level >= 45:
#         return '14286882'
#     return None


# def choose_and_cast_teleport(ensure_tab=True):
#     """Choose the teleport widget for the player's Magic level.

#     - stats_dict: the dict returned by stats()['data'] (or similar shape)
#     - do_click: if True, the function will attempt to open the Magic tab and click the widget
#     - ensure_tab: if True and do_click is True, ensure the Magic tab is open before clicking

#     Returns: (level, widget_id, clicked_bool)
#     """
#     level = get_magic_level_from_stats(stats()['data'])
#     widget = magic_spell_widget_for_level(level)
#     if widget is None:
#         print(f'No teleport widget mapped for Magic level: {level}')
#         exit()

#     print(f'Magic level: {level} -> teleport widget: {widget}')

#     # Ensure the magic tab is open (widget id and sprite check taken from this file comments)
#     if ensure_tab and not check_widget('35913797', sprite_id=1027):
#         click_widget('35913797', rand_x=10, rand_y=10)
#         # small wait for tab to open
#         for _ in range(50):
#             if check_widget('35913797', sprite_id=1027):
#                 break
#             time.sleep(0.05)

#     # perform the click (left-click by default)
#     click_widget(widget)
#     wait_for_tick(4)
#     if random.randint(0, 100) == 0:
#         wait_ticks = random.randint(1, 50)
#         print('Random extra wait for', wait_ticks, 'ticks')
#         wait_for_tick(wait_ticks)

# focus_runelite_window()
# while True:
#     choose_and_cast_teleport()


# check if law runes, are in inventory
# while True:
#     print(get_inventory_count('law rune'))


# while check_inventory('law rune') < 1:
#     print('no law runes in inventory, exiting')
#     exit()
# check magic level
# click teleport spell:
# 25-30 magic: click_widdget('14286871')
# 31-36 magic: click_widget('14286874')
# 37-44 magic: click_widget('14286877')
# 45-99 magic: click_widget('14286882')


# click_gameobject('9730', 'chop down')

# minigame_tab = '35913775'
# minigame_widget = '4980746'
# castle_wars_widget = '4980758', child_index=4

# toggle_prayer(('PROTECT_FROM_RANGE', 'STEEL_SKIN'))


# for i in range(7):
#     click_widget('35913775', rand_x=10, rand_y=10)
#     click_widget('4980746')
#     click_widget_child('4980758', child_index=4)
#     click_widget('4980768')
#     if wait_for_tile_change():
#         break
#     print('unable to teleport to castle wars, sleeping for 3-4min and retrying', i)
#     time.sleep(random.randint(3,4)*60)
    

# # Define the canvas bounds (assuming these apply to the game canvas coordinates for visibility check)
# CANVAS_X_MIN = 4
# CANVAS_X_MAX = 512
# CANVAS_Y_MIN = 4
# CANVAS_Y_MAX = 334
# def click_physical_tile_if_visible(tile_x, tile_y, plane=0, tile_radius=10):
#     """
#     Click the physical tile on the game screen if it's visible within the specified radius and within canvas bounds.
    
#     Args:
#         tile_x (int): Target tile X coordinate.
#         tile_y (int): Target tile Y coordinate.
#         plane (int): Target tile plane (defaults to 0).
#         tile_radius (int): Radius to search around the target tile for visibility (defaults to 10).
    
#     Returns:
#         bool: True if clicked successfully, False otherwise.
#     """
#     # Get tile data around the target with middle point (screen position)
#     tile_data = tile(tile_x=tile_x, tile_y=tile_y, tile_radius=tile_radius, middle_point=True)
#     if not tile_data or 'data' not in tile_data or not tile_data['data']:
#         print(f"No tile data available around ({tile_x}, {tile_y}, {plane})")
#         return False
    
#     # Find the exact target tile in the visible tiles
#     target_info = None
#     for tile_info in tile_data['data']:
#         if tile_info.get('x') == tile_x and tile_info.get('y') == tile_y and tile_info.get('plane') == plane:
#             target_info = tile_info
#             break
    
#     if not target_info:
#         print(f"Target tile ({tile_x}, {tile_y}, {plane}) not visible on screen")
#         return False
    
#     if 'middle_point' not in target_info:
#         print(f"Target tile ({tile_x}, {tile_y}, {plane}) has no middle_point (not visible)")
#         return False
    
#     # Extract canvas coordinates
#     canvas_x = target_info['middle_point']['x']
#     canvas_y = target_info['middle_point']['y']
    
#     # Check if within the canvas bounds (adjusted for physical canvas)
#     if not (CANVAS_X_MIN <= canvas_x <= CANVAS_X_MAX and CANVAS_Y_MIN <= canvas_y <= CANVAS_Y_MAX):
#         print(f"Target tile ({tile_x}, {tile_y}, {plane}) canvas position ({canvas_x}, {canvas_y}) outside bounds")
#         return False
    
#     print(f"Tile ({tile_x}, {tile_y}, {plane}) visible at canvas ({canvas_x}, {canvas_y}), clicking physical position...")
    
#     # Convert to screen coordinates and click
#     screen_x, screen_y = runelite_window(canvas_x, canvas_y)
#     move(screen_x, screen_y, button='left', fast=True, sleep=True)
    
#     # Optional: Wait for the click to register (e.g., one tick)
#     wait_for_tick(1)
    
#     return True

# # Usage: Click the specific physical tile if conditions met
# click_physical_tile_if_visible(2948, 3821)

# # open logout
# _quick_hop = False

# def quickhop_widget():
#     global _quick_hop
#     # checks the logout tab
#     if not _quick_hop:
#         if check_widget('35913778', sprite_id=-1):
#             print('opening logout widget')
#             # opens the logout tab
#             click_widget('35913778', rand_x=10, rand_y=10)
#             # opens the logout widget
#             click_widget('11927559')
#             while not check_widget('4522004'):
#                 time.sleep(0.1)
#             _quick_hop = True
#             return True
#         elif check_widget('11927559'):
#             click_widget('11927559')
#             _quick_hop = True
#             return True
#     return False

# def extract_world_number(text):
#     if text is None:
#         return None
#     match = re.search(r'\d+$', text)
#     if match:
#         return int(match.group())
#     return None

# def get_hop_worlds(membership='p2p'):
#     current_world_text = check_widget_text("4521987")
#     current_world = extract_world_number(current_world_text)
#     min_y = 242
#     max_y = 432
#     color = 15790080 if membership == 'p2p' else 14737632
#     sprite_id = 1131 if membership == 'p2p' else 1130
#     widgets = get_all_widget_data()
#     try:
#         parent = next(w for w in widgets if w['id'] == 4522003)
#     except StopIteration:
#         return []
#     children = parent['children']
#     results = []
#     index = 2
#     while index < len(children):
#         name_child = children[index]
#         sprite_index = index - 1
#         if sprite_index < 0 or sprite_index >= len(children):
#             index += 6
#             continue
#         sprite_child = children[sprite_index]
#         if name_child['textColor'] == color and sprite_child['spriteId'] == sprite_id:
#             # Extract world number from name
#             match = re.search(r'>(\d+)<', name_child['name'])
#             world_num = int(match.group(1)) if match else None
#             if world_num != current_world and min_y <= name_child['random_clickpoint']['y'] <= max_y:
#                 results.append({
#                     'random_clickpoint': name_child['random_clickpoint'],
#                     'name': name_child['name'],
#                     'text': name_child['text']
#                 })
#         index += 6
#     return results

# def hop_to_random_world(membership='p2p'):
#     if not _quick_hop:
#         quickhop_widget()
#         while not check_widget('4522004'):
#             time.sleep(0.05)
#     else:
#         # opens the logout tab
#         click_widget('35913778', rand_x=10, rand_y=10)
#         while not get_hop_worlds(membership):
#             time.sleep(0.01)
    
#     max_scroll_attempts = 10
#     scroll_attempts = 0
#     worlds = get_hop_worlds(membership)

#     while not worlds and scroll_attempts < max_scroll_attempts:
#         print(f"No worlds found, attempting to scroll (attempt {scroll_attempts + 1}/{max_scroll_attempts})")
#         if click_scrollbar():
#             time.sleep(0.05)  # Brief pause to allow the scroll to take effect
#             worlds = get_hop_worlds(membership)
#         else:
#             print("Failed to click scrollbar")
#             time.sleep(0.1)
#         scroll_attempts += 1
    
#     if not worlds:
#         print("world list not found after scrolling attempts: ", worlds)
#         exit()
    
#     world = random.choice(worlds)
#     canvas_x = world['random_clickpoint']['x']
#     canvas_y = world['random_clickpoint']['y']
#     screen_x, screen_y = runelite_window(canvas_x, canvas_y)
#     print(f"Hopping to world: {world['text']}")
#     focus_runelite_window()
#     move(screen_x, screen_y, button='left', fast=True, sleep=True)
#     wait_for_tick(3)
#     while True:
#         state = game_state()
#         if state['data'] == 'LOGGED_IN':
#             time.sleep(0.1)
#             click_scrollbar()
#             break

# def click_scrollbar(parent_id='4522004', max_attempts=10):
#     """
#     Safely clicks in the child_index=0 widget of the parent, avoiding the y-bounds of child_index=1.
    
#     :param parent_id: The ID of the parent widget.
#     :param max_attempts: Maximum attempts to find a safe click point before giving up.
#     """
#     # Get the child1 widget to determine the forbidden y area
#     child1 = get_widget(parent_id, child_index=1)
#     forbidden_y = child1['bounds']['y']  # Top y of the small widget (e.g., button)
    
#     lower_tolerance = 1
#     upper_tolerance = 13
    
#     attempts = 0
#     while attempts < max_attempts:
#         # Get a random point in the large child0 area
#         child0 = get_widget(parent_id, child_index=0)
#         click_x, click_y = runelite_window(child0['random_clickpoint']['x'], child0['random_clickpoint']['y'])
#         # Check if the click_y is outside the forbidden zone
#         if not (forbidden_y - lower_tolerance <= click_y <= forbidden_y + upper_tolerance):
#             # Safe to click: move and left-click smoothly
#             move(x=click_x, y=click_y, button='left', fast=True, sleep=True)
#             print(f"Safe click performed at ({click_x}, {click_y})")
#             return True
        
#         attempts += 1
#         # Small delay to avoid rapid calls
#         time.sleep(0.1)
    
#     print(f"Failed to find a safe click point after {max_attempts} attempts. Forbidden y: {forbidden_y} ± ({lower_tolerance}, {upper_tolerance})")
#     return False



# click_scrollbar()
# current_tick = gametick().get('data', 0)
# print(current_tick)

# hop_to_random_world()



# print(check_widget('4522003', child_index=1, sprite_id=1130))

# print(get_widget('4522004', child_index=1))
# print(get_widget('4522004', child_index=0))

# hop_to_random_world()
# print(get_hop_worlds())


# def check_hop_screen():
#     index = 2
#     while index < 1853:
#         if not check_widget_text('4522003', child_index=index):
#             return False
#         index += 6
#     return True

# print(check_hop_screen())

# click_object('1524', 'open')
# print(fetch_object('1540', 'Open', 2603, 3082))



# waypoints = [(3006, 3821), (2976, 3820), (2959, 3820)]  # Add ,0 to last if needed

# for waypoint in waypoints:
#     success = False
#     for _ in range(12):
#         if click_minimap_tile(*waypoint, target_zoom=2):
#             success = True
#             break
#         wait_for_tick(1)
#     if not success:
#         break  # Stop progression if this level failed


# click_inventory('burning amulet(4)', action='Wear')
# click_equipment_item('staff of air', action='examine')

# print(check_widget_text('10485796'))

# camera(339, 2017, 534)
# print(pick(2950, 3824, size=10, item='Wine of zamorak'))


# from modules.utils.check_if_in_area import check_if_in_area

# print(check_if_in_area(
# ["3214,3221,0",
# "3214,3211,0",
# "3227,3211,0",
# "3227,3226,0",
# "3217,3226,0",
# "3214,3221,0"]))

# print(players(radius=10))

# print(players(radius=6))
# def check_high_reward_points(widget_id, child_index=6, threshold=3000000):
#     text = check_widget_text(widget_id, child_index=child_index)
#     if 'Reward points:' in text:
#         points_str = text.split('Reward points: ')[1].strip()
#         points = int(points_str.replace(',', ''))
#         return points > threshold
#     return False

# # Usage example
# result = check_high_reward_points('13500418', threshold=4000)
# print(result)

# combat_style('rapid')

# print(tile(tile_radius=0))

# print(check_widget_text('10485796'))

# print(check_inventory("overload (4)"))


# def is_player_idle():
#     """
#     Check if the player is idle (not moving) based on animation and tile stability.
    
#     Returns:
#     - True if player's tile hasn't changed in the last tick and animation is idle, False otherwise.
#     """
#     pl_data = player(location=True, animation=True)
#     if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data'] or 'animation' not in pl_data['data']:
#         print("Failed to fetch player location or animation")
#         return False
    
#     initial_loc = pl_data['data']['location']
#     initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
#     animation = pl_data['data']['animation']
    
#     wait_for_tick(ticks=1)
    
#     pl_data = player(location=True, animation=True)
#     if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
#         print("Failed to fetch player location after tick")
#         return False
    
#     current_loc = pl_data['data']['location']
#     current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
    
#     is_idle = current_tile == initial_tile and pl_data['data']['animation'] in [0, -1]
#     print(f"Player idle check: Tile unchanged: {current_tile == initial_tile}, Animation: {pl_data['data']['animation']}, Idle: {is_idle}")
#     return is_idle

# def check_if_in_tile(x, y, plane=0, click=False, right_click=False):
#     """
#     Check if the player is standing on the specific tile.
    
#     Parameters:
#     - x: Tile x-coordinate.
#     - y: Tile y-coordinate.
#     - plane: Tile plane (defaults to 0).
#     - click: If True, click the tile on minimap if visible and walkable, if not on tile.
    
#     Returns:
#     - True if on tile (or successfully moved to it), False otherwise.
    
#     From different views:
#     - Functionality: Compares player tile to target; clicks exact visible walkable tile.
#     - Reliability: Waits for idle state before retrying, uses 5 retries and walkable checks.
#     - Performance: Checks if target tile is visible on minimap, no bounding box needed.
#     - Bigger picture: Ensures exact positioning in RuneScape for tasks like precise interactions or safe spots.
#     """
#     target_tile = (x, y, plane)
#     print(f"Target tile: {target_tile}")

#     # Get initial player position
#     pl_data = player(location=True)
#     if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
#         print("Failed to fetch player location")
#         return False
#     loc = pl_data['data']['location']
#     px, py, pplane = loc['x'], loc['y'], loc['plane']
#     player_tile = (px, py, pplane)
#     print(f"Initial player location: {player_tile}")

#     # Check if player is on the target tile
#     if player_tile == target_tile:
#         print("Player is on the target tile")
#         return True

#     if not click:
#         print("Player not on tile, click=False, returning False")
#         return False

#     # Attempt to move to tile, max 5 tries
#     max_tries = 5
#     for attempt in range(max_tries):
#         print(f"Attempt {attempt + 1}/{max_tries} to move to tile")
#         # Get current player position
#         pl_data = player(location=True, animation=True)
#         if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
#             print("Failed to fetch player location during attempt")
#             return False
#         loc = pl_data['data']['location']
#         px, py, pplane = loc['x'], loc['y'], loc['plane']
#         print(f"Current player position: ({px}, {py}, {pplane})")

#         # Check if player is already on the tile before clicking
#         if (px, py, pplane) == target_tile:
#             print("Player is on the target tile after position check")
#             return True

#         # Get visible minimap tiles
#         mm_data = minimap_tiles().get('data', [])
#         if not mm_data:
#             print("No minimap tiles data available")
#             return False

#         # Check if target tile is visible and walkable
#         is_visible = False
#         for entry in mm_data:
#             if entry['tileX'] == x and entry['tileY'] == y:
#                 is_visible = True
#                 break
#         if not is_visible:
#             print(f"Target tile ({x}, {y}, {plane}) not visible on minimap")
#             return False

#         walkable_data = walkable_tile(x, y, tile_radius=20, middle_point=False)
#         if not walkable_data or not walkable_data.get('data', []):
#             print(f"Target tile ({x}, {y}, {plane}) is not walkable")
#             return False
#         print(f"Target tile ({x}, {y}, {plane}) is walkable, distance: {math.hypot(x - px, y - py):.2f} tiles")

#         # Click the exact tile
#         if not click_minimap_tile(x, y, rand_x=0, rand_y=0, right_click=right_click):
#             print("Failed to click minimap tile")
#             return False

#         # Wait for tile change, short timeout
#         print("Waiting for tile change")
#         if not wait_for_tile_change(timeout_ticks=1):  # ~0.6 seconds
#             print("Tile did not change after click")
#             print("Waiting for player to stop moving before retry")
#             while not is_player_idle():
#                 print("Player still moving, waiting another tick")
#             continue

#         # Check if now on tile
#         pl_data = player(location=True)
#         if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
#             print("Failed to fetch player location after move")
#             continue
#         loc = pl_data['data']['location']
#         px, py, pplane = loc['x'], loc['y'], loc['plane']
#         new_tile = (px, py, pplane)
#         print(f"New player location after move: {new_tile}")
#         if new_tile == target_tile:
#             print("Successfully moved to target tile")
#             return True

#         # Wait until player is idle before retrying
#         print("Player moved but not on tile, waiting for idle before retry")
#         while not is_player_idle():
#             print("Player still moving, waiting another tick")

#     print(f"Failed to move to tile after {max_tries} attempts")
#     return False

# walkable_data = walkable_tile(2608, 3115, tile_radius=5, middle_point=False)
# print(walkable_data)

# Example usage:
# check_if_in_tile(2196, 3811, 0, click=True, right_click=True)
# or check_if_in_tile(2196, 3811, click=True)  # plane defaults to 0
# click_minimap_tile(11696, 3559, 0, 0, target_zoom=2)