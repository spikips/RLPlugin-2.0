import time, re, random, math
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
from modules.utils.check_if_in_tile import check_if_in_tile
from modules.utils.inventory import check_inventory, get_inventory_count, click_inventory_sequence
from modules.widgets.widget import check_widget_text, click_widget, check_widget_name, check_widget, get_widget, click_widget_child
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

vine_ids = ['13847', '13848', '13849']  # List of all possible vine IDs to try

while get_inventory_count('short vine') < 3:
    increased = False
    for vine_id in vine_ids:
        old_count = get_inventory_count('short vine')
        click_vine = click_gameobject(vine_id, 'Cut-vine')
        if not click_vine:
            continue  # Try next vine ID if click failed
        
        # Wait to see if count changed (with timeout to avoid infinite loop)
        for _ in range(20):  # Adjust attempts as needed (e.g., 20 * 0.1s = 2s timeout)
            time.sleep(0.1)
            if get_inventory_count('short vine') > old_count:
                increased = True
                break
        if increased:
            break  # Successfully cut a vine, proceed to next one needed
        # If not increased after timeout, try next ID
    
    if not increased:
        # No vine was cut after trying all, perhaps none available
        print("No vines could be cut; stopping.")
        break

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