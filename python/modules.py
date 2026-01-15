#---#
# core/mouse_control.py
from modules.core.mouse_control import move, move_mouse, get_cursor_pos, click_down, click_up, left_click, right_click, middle_click, scroll

# Example for move_mouse(x, y)
# Moves the mouse cursor directly to the specified screen coordinates (e.g., 100, 200)
move_mouse(100, 200)

# Example for get_cursor_pos()
# Retrieves the current mouse cursor position as a tuple (x, y)
current_pos = get_cursor_pos()
print(f"Current mouse position: {current_pos}")

# Example for click_down(button)
# Presses down the specified mouse button without releasing it
# Valid buttons: 'left', 'middle', 'right'
click_down('left')  # Press down left mouse button

# Example for click_up(button)
# Releases the specified mouse button
# Valid buttons: 'left', 'middle', 'right'
click_up('left')  # Release left mouse button

# Example for left_click()
# Performs a full left mouse click (down + up with a short delay)
left_click()

# Example for right_click()
# Performs a full right mouse click (down + up with a short delay)
right_click()

# Example for middle_click()
# Performs a full middle mouse click (down + up with a short delay)
middle_click()

# Example for scroll(direction, sleep=0.1)
# Scrolls the mouse wheel up (positive direction) or down (negative)
# direction: int (positive for up, negative for down)
# sleep: optional float for delay after scroll
scroll(1)  # Scroll up by one notch
scroll(-1, sleep=0.2)  # Scroll down by one notch with 0.2s delay

# Example for move(x=None, y=None, fast=False, button=None, drag=False, speed=2, sleep=False)
# This is a versatile function that can move the mouse, click, or drag
# Move to (300, 400) slowly (human-like curve) without clicking
move(x=300, y=400)

# Move to (500, 600) fast (direct) and perform a left click
move(x=500, y=600, fast=True, button='left')

# Drag from current position to (700, 800) with right button, slowly
move(x=700, y=800, drag=True, button='right')

# Just perform a middle click without moving
move(button='middle')

# Move fast to (900, 1000) with a short sleep after
move(x=900, y=1000, fast=True, sleep=True)

#---#
# core/window_utils.py
from modules.core.window_utils import runelite_window, focus_runelite_window
# Example for focus_runelite_window()
# Brings the RuneLite window to the foreground if not already focused.
# Returns True if successful, False otherwise.
success = focus_runelite_window()
if success:
    print("RuneLite window focused successfully.")
else:
    print("Failed to focus RuneLite window.")

# Example for runelite_window(x: int, y: int) -> tuple[int, int]
# Converts canvas coordinates (e.g., 100, 200) to screen coordinates relative to the RuneLite game canvas.
# If the canvas is not found, returns the original (x, y).
screen_x, screen_y = runelite_window(100, 200)
print(f"Screen coordinates: ({screen_x}, {screen_y})")

#---#
# fetch_data/fetch_bank_items.py
from modules.fetch_data.fetch_bank_items import load_bank_items, fetch_bank_items

# Note: This module relies on a specific JSON file at BANK_CACHE_PATH = r"C:\Users\Asd\source\repos\runelite_plugin\modules\fetch_data\bank\bank_items.json"
# Ensure this file exists and is populated with valid JSON data in the format of a list of dicts, each with 'name' (str) and 'quantity' (int).
# The functions are designed for a RuneLite plugin context, checking bank items in Old School RuneScape or similar.

# Example for load_bank_items() -> Optional[List[Dict[str, any]]]
# Loads the bank items from the JSON cache file.
# Returns a list of item dicts or None if there's an error (e.g., file not found or invalid JSON).
bank_item = load_bank_items()
if bank_item is not None:
    print(f"Loaded {len(bank_item)} bank items.")
    # Example output: [{'name': 'Rune scimitar', 'quantity': 1}, {'name': 'Prayer potion(4)', 'quantity': 10}, ...]
else:
    print("Failed to load bank items.")

# Example for fetch_bank_items(items_to_check: List[Tuple[str, int]]) -> bool
# Checks if the specified items exist in the bank with at least the given quantities.
# Item names are case-insensitive.
# Returns True if all items meet the quantity requirements, False otherwise.
items_to_check = [("rune scimitar", 1), ("prayer potion(4)", 5)]
has_items = fetch_bank_items(items_to_check)
if has_items:
    print("All required items are available in sufficient quantities.")
else:
    print("Missing some required items or quantities.")

#---#
# npc_data/click_npc.py
from modules.npc_data.click_npc import get_player_position, click_npc, click_closest_npc

# Note: This module is designed for interaction with NPCs in Old School RuneScape via a RuneLite plugin.
# It relies on external modules like modules.core.plugin_client (for npc and player data) and modules.utils.select_menu_option.
# Functions fetch real-time game data and perform mouse actions. Ensure the RuneLite client is running and properly configured.
# Coordinates are in world/tile space for distances and screen space for clicks.

# Example for get_player_position()
# Retrieves the local player's world position as (x, y, z). Returns (0, 0, 0) if data is invalid.
player_pos = get_player_position()
print(f"Player position: {player_pos}")

# Example for click_npc(identifier, option=None, max_attempts=3)
# Clicks a single NPC by ID (int) or exact name (str). Optionally selects a menu option.
# Returns True on success, False after max_attempts.
success = click_npc(1567, 'Escort')  # Click NPC with ID 1567 and select 'Escort'
if success:
    print("NPC clicked successfully.")
else:
    print("Failed to click NPC.")

# Alternative: Basic click without option
click_npc('Dominic Onion')  # Basic click on NPC named 'Dominic Onion'

# Example for click_closest_npc(ids_or_name, option=None, max_attempts=3)
# Clicks the closest NPC matching a list of IDs or a partial name (str, case-insensitive).
# Optionally selects a menu option. Returns True on success, False otherwise.
escort_ids = [1566, 1567, 1578, 1577]
success = click_closest_npc(escort_ids, 'Escort')  # Click closest from ID list and select 'Escort'
if success:
    print("Closest NPC clicked successfully.")
else:
    print("Failed to click closest NPC.")

# Alternative: Name-based search
click_closest_npc('undead lumberjack', 'attack')  # Click closest 'undead lumberjack' and select 'attack'

#---#
# npc_data/check_npc_animation.py
from modules.npc_data.check_npc_animation import check_npc_animation

# Note: This module checks NPC animations in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for npc and player data) and modules.core.window_utils.
# Animation IDs are game-specific (e.g., 4659 for dying moss giant). Tile radius limits search area.

# Example for check_npc_animation(animation_id: int, npc_name: str, tile_radius: int = 10) -> bool
# Checks if any NPC with the given name within tile_radius has the specified animation ID.
# Returns True if found, False otherwise.
is_dying = check_npc_animation(4659, 'moss giant')
print(f"Is moss giant dying? {is_dying}")

# With custom tile_radius
check_npc_animation(4659, 'moss giant', tile_radius=15)

#---#
# npc_data/wait_npc_animation.py
from modules.npc_data.wait_npc_animation import wait_for_npc_animation

# Note: This module waits for NPC animations in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for npc and player data).
# Polls at check_interval until timeout or animation is detected. Tile radius limits search area.

# Example for wait_for_npc_animation(animation_id: int, npc_name: str, tile_radius: int = 10, timeout: float = 30.0, check_interval: float = 0.5) -> bool
# Waits for any NPC with the given name within tile_radius to enter the specified animation ID.
# Returns True if detected within timeout, False otherwise.
waited = wait_for_npc_animation(4659, 'moss giant')
print(f"Waited for moss giant animation: {waited}")

# With custom parameters
wait_for_npc_animation(4659, 'moss giant', tile_radius=15, timeout=60.0, check_interval=1.0)

#---#
# npc_data/wait_npc_animation.py
from modules.npc_data.wait_npc_animation import wait_for_npc_animation

# Note: This module waits for NPC animations in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for npc and player data).
# Polls at check_interval until timeout or animation is detected. Tile radius limits search area.

# Example for wait_for_npc_animation(animation_id: int, npc_name: str, tile_radius: int = 10, timeout: float = 30.0, check_interval: float = 0.5) -> bool
# Waits for any NPC with the given name within tile_radius to enter the specified animation ID.
# Returns True if detected within timeout, False otherwise.
waited = wait_for_npc_animation(4659, 'moss giant')
print(f"Waited for moss giant animation: {waited}")

# With custom parameters
wait_for_npc_animation(4659, 'moss giant', tile_radius=15, timeout=60.0, check_interval=1.0)

#---#
# object_data/object.py
from modules.object_data.object import get_objects, get_closest_object, check_object, click_object, use_on_object

# Note: This module fetches and interacts with local objects in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for fetch_object and player data), modules.core.window_utils, and modules.utils.select_menu_option.
# Object identifiers can be strings (names) or IDs. Actions are required for filtering. Searches are player-centered unless a tile is specified.
# Coordinates: World tiles for distances, canvas/screen for interactions. Clicks are bounded to canvas area.

# Example for get_objects(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> List[Dict[str, Any]]
# Fetches local objects matching identifier and action within radius.
# Returns a list of object dicts or empty list if none found.
objects = get_objects("Tree", "Chop down")  # Trees with 'Chop down' action near player
print(f"Found {len(objects)} choppable trees.")

# With specific tile and radius
specific_tile = (3200, 3200)  # Example world tile (x, y)
objects_at_tile = get_objects("Door", "Open", tile=specific_tile, radius=5)
print(objects_at_tile)  # List of dicts with tile, middle_point, actions, etc.

# Example for get_closest_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> Optional[Dict[str, Any]]
# Gets the closest matching local object within canvas bounds. Returns dict or None.
closest = get_closest_object("Bank booth", "Bank")
if closest:
    print(f"Closest bank booth at tile ({closest['tile']['x']}, {closest['tile']['y']})")
else:
    print("No bank booth found.")

# Example for check_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> bool
# Checks if a matching local object exists within radius and canvas bounds.
exists = check_object("Tree", "Chop down")
print(f"Choppable tree nearby: {exists}")

# Example for click_object(object_identifier: str, action: str, tile: Optional[Tuple[int, int]] = None, radius: int = 20) -> bool
# Clicks the specified action on the closest local object. Returns True if successful.
clicked = click_object("Bank booth", "Bank")
if clicked:
    print("Clicked 'Bank' on bank booth.")
else:
    print("Failed to click on bank booth.")

# Example for use_on_object(object_identifier: str, action: str, use_option: str, tile: Optional[Tuple[int, int]] = None, radius: int = 6) -> bool
# Finds object with base action, then selects a different use_option (e.g., for item use).
# Returns True if successful.
used = use_on_object("Fountain", "Drink", "Use Potion -> Fountain")  # Example: Base 'Drink', select 'Use Potion -> Fountain'
if used:
    print("Used item on fountain.")
else:
    print("Failed to use on fountain.")

#---#
# player_data/wait_till_character_stops_moving.py
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving

# Note: This module waits for the player character to stop moving in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for player data) and modules.utils.wait_for_tick.
# Checks tile position and animation (0 or -1 for idle). Polls every tick.

# Example for wait_till_character_stopped_moving(max_ticks: int = 100, required_idle_ticks: int = 1)
# Waits until player is idle for required consecutive ticks. Returns True if idle, False on timeout.
stopped = wait_till_character_stopped_moving()
if stopped:
    print("Player has stopped moving.")
else:
    print("Timeout waiting for player to stop.")

# With custom parameters
wait_till_character_stopped_moving(max_ticks=50, required_idle_ticks=3)

#---#
# player_data/tile_change.py
from modules.player_data.tile_change import wait_for_tile_change

# Note: This module waits for the player's tile to change in Old School RuneScape via a RuneLite plugin.
# It relies on modules.utils.wait_for_tick and modules.core.plugin_client (for player data).
# Includes retries for location fetches. Raises ValueError on persistent failures.

# Example for wait_for_tile_change(timeout_ticks=20, max_retries=3)
# Waits for player's tile to change. Returns True if changed, False on timeout.
changed = wait_for_tile_change()
if changed:
    print("Tile has changed.")
else:
    print("Timeout waiting for tile change.")

# With custom parameters
wait_for_tile_change(timeout_ticks=30, max_retries=5)

#---#
# player_data/check_run.py
from modules.player_data.check_run import click_run

# Note: This module toggles run/walk mode in Old School RuneScape via a RuneLite plugin.
# It relies on modules.widgets.widget (for click_widget).
# Clicks the run orb widget based on sprite ID (1069 for off, 1070 for on).

# Example for click_run(enable=True)
# Enables run if off, or prints if already enabled. For disable, set enable=False.
click_run(enable=True)  # Enable run
click_run(enable=False)  # Disable run (enable walk)

#---#
# player_data/cannon.py
from modules.player_data.cannon import click_cannon

# Note: This module interacts with the dwarf multicannon in Old School RuneScape via a RuneLite plugin.
# It relies on modules.object_data.game_object (get_closest_game_object), modules.core.plugin_client (cannon_data, reset_cannon), modules.core.mouse_control (move), modules.core.window_utils (runelite_window), modules.utils.select_menu_option (select_menu_option).
# Clicks cannon with action, falls back to game object query if middle_point missing. Cannon IDs: [6,7,8,9].

# Also imports but unused in provided code: get_varbits

# Example for click_cannon(action: str = 'Fire') -> bool
# Performs action on cannon (e.g., 'Fire' to reload, 'Pick-up'). Returns True if successful.
success = click_cannon('Fire')
if success:
    print("Cannon reloaded.")
else:
    print("Failed to interact with cannon.")

# Other actions
click_cannon('Pick-up')

# Test cannon data (from code comment)
# print("Current cannon data:")
# print(cannon_data().get('data', {}))
# prints something like: {'data': {'ammo': 0, 'exists': False, 'id': -1}} or {'data': {'ammo': 0, 'exists': True, 'position': 'WorldPoint(x=1434, y=9886, plane=0)', 'id': -1}}


# Optional reset (from code comment)
# reset_cannon()
# print("Cannon data after reset:")
# print(cannon_data().get('data', {}))

#---#
# player_data/get_level.py
from modules.player_data.get_level import get_level

# Note: This module retrieves player skill levels in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for stats).
# Skill names are case-insensitive, capitalized internally. Raises ValueError on errors.

# Example for get_level(skill)
# For single skill (str): Returns int level.
magic_level = get_level('magic')
print(f"Magic level: {magic_level}")

# For multiple skills (list): Returns dict of {skill: level}.
levels = get_level(['woodcutting', 'magic', 'defence'])
print(levels)

#---#  
# player_data/click_equipment.py
from modules.player_data.click_equipment import click_equipment_item

# Note: This module clicks equipped items in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for gear), modules.widgets.widget, and modules.core.window_utils.
# Partial name match (case-insensitive). Optional action for menu selection or right-click.

# Example for click_equipment_item(item_name: str, action: str = None, right_click: bool = False)
# Clicks item, optionally selects action or just right-clicks. Returns True if successful.
success = click_equipment_item("Ring of dueling", "Ferox Enclave")
if success:
    print("Teleported to Ferox Enclave.")
else:
    print("Failed to click ring.")

# Basic left-click
click_equipment_item("Staff of air")

# Right-click without action
click_equipment_item("Staff of air", right_click=True)

# With action
click_equipment_item("Staff of air", action='Examine')

#---#
# player_data/prayer/check_prayer_book.py
from modules.player_data.prayer.check_prayer_book import check_prayer_spellbook

# Note: This module checks and opens the prayer spellbook in Old School RuneScape via a RuneLite plugin.
# It relies on modules.widgets.widget_data (for get_all_widget_data), modules.core.mouse_control, and modules.core.window_utils.
# Widget ID 35913797, SpriteId 1030 for open, -1 for closed. Clicks random point in bounds to open.

# Example for check_prayer_spellbook()
# Checks if prayer spellbook is open; opens it if not. Returns True if open or opened successfully, False otherwise.
is_open = check_prayer_spellbook()
if is_open:
    print("Prayer spellbook is open.")
else:
    print("Failed to open prayer spellbook.")

#---#
# player_data/prayer/toggle_prayer.py
from modules.player_data.prayer.toggle_prayer import check_prayer, toggle_prayer

# Note: This module checks and toggles prayers in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (for get_active_prayers), modules.player_data.prayer.check_prayer_book, modules.widgets.widget_data, modules.core.mouse_control, modules.core.window_utils, and keyboard.
# Supported prayers in PRAYER_WIDGETS: 'PROTECT_FROM_MELEE', 'PROTECT_FROM_RANGE', 'STEEL_SKIN'. Add more as needed.
# Toggles by clicking widget centers; presses F1 after toggle.

# Example for check_prayer(prayer_name: str = 'PROTECT_FROM_MELEE') -> bool
# Checks if the specified prayer is active. Returns True if active, False otherwise.
is_active = check_prayer('PROTECT_FROM_MELEE')
print(f"Protect from Melee active: {is_active}")

# With different prayer
check_prayer('STEEL_SKIN')

# Example for toggle_prayer(prayer_names, activate: bool = True) -> bool
# Toggles one or more prayers to active (True) or inactive (False). Returns True if successful or already in state.
success = toggle_prayer('PROTECT_FROM_RANGE')  # Activate single prayer
if success:
    print("Toggled successfully.")
else:
    print("Failed to toggle.")

# Multiple prayers
toggle_prayer(['PROTECT_FROM_RANGE', 'STEEL_SKIN'], activate=False)  # Deactivate list

# Tuple
toggle_prayer(('PROTECT_FROM_MELEE', 'STEEL_SKIN'))

#---#  
# utils/hop.py
from modules.utils.hop import quickhop_widget, logout_widget, extract_world_number, get_hop_worlds, hop_to_random_world, click_scrollbar

# Note: This module handles world hopping in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (game_state), modules.utils.wait_for_tick, modules.widgets.widget (check_widget_text, click_widget, check_widget, get_widget), modules.core.mouse_control (move), modules.widgets.widget_data, modules.core.window_utils (runelite_window, focus_runelite_window), keyboard, time, re, random.
# Opens hop widget, extracts worlds, scrolls if needed, hops to random or visible worlds. Membership: 'p2p' (default), others implied.

# Example for quickhop_widget() -> bool
# Opens the quick hop widget if not already open. Sets global _quick_hop.
opened = quickhop_widget()
if opened:
    print("Quick hop widget opened.")
else:
    print("Already open or failed.")

# Example for logout_widget()
# Opens the logout widget and hop widget using F5 if needed.
logout_widget()

# Example for extract_world_number(text) -> int or None
# Extracts world number from text (e.g., 'World 301' -> 301).
world = extract_world_number("World 301")
print(f"World number: {world}")

# Example for get_hop_worlds(membership='p2p') -> dict or None
# Gets a random visible hop world dict (clickpoint, name, etc.) filtered by membership, excluding PVP/high risk.
world_data = get_hop_worlds('p2p')
if world_data:
    print(f"World data: {world_data}")
else:
    print("No suitable world found.")

# Example for hop_to_random_world(membership='p2p')
# Hops to a random suitable world, opening widget and scrolling if needed. Waits for login.
hop_to_random_world('p2p')

# Example for click_scrollbar(membership='p2p', parent_id='4522004', max_attempts=10) -> bool
# Clicks scrollbar safely to load worlds until one is found or max attempts reached.
scrolled = click_scrollbar(membership='p2p')
if scrolled:
    print("Scrolled successfully.")
else:
    print("Failed to find world after scrolling.")

#---#  
# utils/logout.py
from modules.utils.logout import check_login_state_and_login, logout_and_break, logout

# Note: This module handles logout and timed breaks in Old School RuneScape via a RuneLite plugin.
# It relies on time, random, datetime, modules.core.plugin_client (game_state), modules.core.mouse_control (mouse), modules.core.window_utils (runelite_window), modules.widgets.widget (click_widget).
# Uses hardcoded screen coordinates relative to RuneLite window for clicks. Polls game state for login/logout detection.
# Exits on timeout failures.

# Example for check_login_state_and_login() -> bool
# Checks if at login screen and performs login clicks if so. Returns True if successful, False otherwise. Exits on timeout.
logged_in = check_login_state_and_login()
if logged_in:
    print("Logged in successfully.")
else:
    print("Not at login screen or failed.")

# Example for logout_and_break(break_minutes: int)
# Logs out (retries up to ~3 times), waits break_minutes * 60 seconds, logs back in. Prints timestamps. Exits on login timeout.
logout_and_break(69)  # 69-minute break

logout()  # Simple logout without break
#---#  
# utils/humanlike_interact.py
from modules.utils.humanlike_interact import get_widget_bounds, random_tab_click, random_right_click_area, perform_humanlike_interaction

# Note: This module simulates human-like interactions in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.mouse_control, modules.core.window_utils, modules.widgets.widget_data, modules.utils.wait_for_tick, random, time.
# Clicks random tabs (e.g., combat, stats) or right-clicks safe areas with mouse movement. Probabilities: 20% skip, 80% tab or right-click.

# Example for get_widget_bounds(widget_id: int) -> tuple[int, int, int, int] | None
# Gets bounds (x, y, width, height) of a widget by ID.
bounds = get_widget_bounds(35913792)  # Combat tab
print(f"Bounds: {bounds}")

# Example for random_tab_click() -> bool
# Clicks a random tab and returns to inventory. Returns True if performed.
performed = random_tab_click()
print(f"Tab click performed: {performed}")

# Example for random_right_click_area() -> bool
# Right-clicks a random safe point on screen, moves mouse naturally. Returns True if performed.
performed = random_right_click_area()
print(f"Right-click performed: {performed}")

# Example for perform_humanlike_interaction() -> None
# Decides and performs a random human-like action (tab click or right-click).
perform_humanlike_interaction()

#---#  
# utils/loot.py
from modules.utils.loot import normalize_item_name, clean_target_name, can_pick_item, wait_for_next_tick, pickup_closest_ground_item, loot_all_ground_items

# Note: This module handles ground item looting in Old School RuneScape via a RuneLite plugin.
# It relies on modules.player_data.wait_till_character_stops_moving, modules.core.plugin_client (player, pick, interact_options, gametick, inventory), modules.core.mouse_control, modules.core.window_utils, time, random.
# Normalizes names, checks space, waits ticks, picks closest or all matching items within radius.

# Example for normalize_item_name(name: str) -> str
# Normalizes item name by removing dose indicators.
norm = normalize_item_name("Prayer potion(4)")
print(f"Normalized: {norm}")

# Example for clean_target_name(target: str) -> str
# Cleans menu target by removing color tags and quantity.
clean = clean_target_name("<col=ff9040>Prayer potion</col> x 5")
print(f"Cleaned: {clean}")

# Example for can_pick_item(item_name: str) -> bool
# Checks if inventory has space or item stacks.
can_pick = can_pick_item("Coins")
print(f"Can pick: {can_pick}")

# Example for wait_for_next_tick(num_ticks: int = 1) -> None
# Waits for specified game ticks.
wait_for_next_tick(2)

# Example for pickup_closest_ground_item(item_name: str, tile_radius: int = 10, max_attempts: int = 3, wait_ticks: int = 3) -> bool
# Picks up the closest matching ground item. Returns True if successful.
picked = pickup_closest_ground_item("Mark of grace", tile_radius=15)
print(f"Picked up: {picked}")

# Example for loot_all_ground_items(item_name: str, tile_radius: int = 10, delay_range: tuple = (0.2, 0.4)) -> int
# Loots all matching ground items, returns count.
count = loot_all_ground_items("Bones", delay_range=(0.3, 0.6))
print(f"Looted {count} items.")

#---#  
# utils/inventory.py
from modules.utils.inventory import click_inventory, get_inventory_count, check_inventory, drop_inventory, click_inventory_sequence

# Note: This module manages inventory interactions in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (inventory), modules.core.mouse_control, modules.core.window_utils, modules.widgets.widget, modules.utils.select_menu_option, modules.utils.wait_for_tick, random, keyboard, time, re.
# Clicks items with optional actions, counts, checks presence, drops, sequences clicks.

# Example for click_inventory(item: str, action: Optional[str] = None, hover_only: bool = False) -> bool
# Clicks item in inventory, optionally with action or hover.
success = click_inventory("Prayer potion", "Drink")
print(f"Success: {success}")

# Basic left-click
click_inventory("Lobster")

# Hover only with action
click_inventory("Ring of wealth", "Rub", hover_only=True)

# Example for get_inventory_count(item: str, exact_match: bool = False) -> int
# Counts quantity of item in inventory.
count = get_inventory_count("Coins")
print(f"Count: {count}")

# Exact match
get_inventory_count("Prayer potion(4)", exact_match=True)

# Example for check_inventory(item: str, exact_match: bool = False) -> bool
# Checks if item is in inventory.
has_item = check_inventory("Shark")
print(f"Has item: {has_item}")

# Example for drop_inventory(item: str, quantity: Union[str, int] = 'all') -> bool
# Drops specified quantity of item ('all', 'x', or int).
dropped = drop_inventory("Logs", 10)
print(f"Dropped: {dropped}")

# Drop all
drop_inventory("Bones", 'all')

# Example for click_inventory_sequence(items: List[str], action: Optional[str] = None, delay: float = 0.3) -> bool
# Clicks a sequence of items, optionally with action.
success = click_inventory_sequence(["Knife", "Logs"], "Use", delay=0.5)
print(f"Sequence success: {success}")

#---#  
# utils/varbit_change.py
# from modules.utils.varbit_change import varbit_change
# Note: This is a script that polls for varbit changes in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (varbit_changes), time.
# No functions defined; runs a loop printing changes every tick (0.6s).

# Example usage: Run the script to monitor varbit changes.
# while True:
#     changes = varbit_changes()
#     if changes and 'data' in changes:
#         for change in changes['data']:
#             print(f"Varbit {change['varbit']} changed: {change['old']} -> {change['new']} (tick {change['tick']})")
#     time.sleep(0.6)

#---#  
# utils/wait_for_tick.py
from modules.utils.wait_for_tick import wait_for_tick, wait_for_next_tick

# Note: This module waits for game ticks in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (gametick), time.
# Polls frequently (0.01s or 0.05s) until tick advances.

# Example for wait_for_tick(ticks=1)
# Waits for exactly the specified ticks. Returns True.
wait_for_tick(2)

# Example for wait_for_next_tick(num_ticks: int = 1) -> None
# Waits for the next specified ticks.
wait_for_next_tick(3)

#---#  
# utils/select_menu_option.py
from modules.utils.select_menu_option import select_menu_option

# Note: This module selects menu options in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.window_utils, modules.core.plugin_client (interact_options), modules.core.mouse_control, time, random, re.
# Hovers at (x,y), right-clicks if needed, selects action (exact or combined with target). Optional hover only.

# Example for select_menu_option(x: int, y: int, action: str, hover_only: bool = False) -> Optional[Dict[str, Any]]
# Selects the action at canvas coordinates. Returns option dict or None.
option = select_menu_option(249, 140, "Take absorption potion")
print(f"Selected: {option}")

# Hover only
select_menu_option(100, 200, "Climb ladder", hover_only=True)

#---#  
# utils/spec.py
from modules.utils.spec import spec

# Note: This module handles special attack in Old School RuneScape via a RuneLite plugin.
# It relies on modules.widgets.widget, modules.utils.wait_for_tick.
# Checks spec energy, enables if >= threshold and not already on.

# Example for spec(threshold=50)
# Enables special attack if energy >= threshold. Returns True if successful or not needed.
used = spec(100)  # For dragon dagger p++
print(f"Spec used: {used}")

#---#  
# utils/camera.py
from modules.utils.camera import scroll_to_zoom, camera

# Note: This module adjusts the RuneScape camera (pitch, yaw, zoom) in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (player, game_state), modules.core.mouse_control (move, get_cursor_pos, scroll), modules.core.window_utils (runelite_window), time, random.
# scroll_to_zoom uses predefined ZOOM_LEVELS and scrolls with speed control (1-10). camera() ensures zoom >=300 first, then drags middle mouse in passes (up to 20) using 1:2 pixel-to-unit ratio for pitch/yaw. Final zoom set even if rotation fails.

# Example for scroll_to_zoom(target_zoom: int, max_retries: int = 30, speed: int = 10) -> bool
# Adjusts camera zoom to target level (61-1940) with retries and speed control. Moves mouse to random client point first.
zoomed = scroll_to_zoom(620, max_retries=20, speed=5)
if zoomed:
    print("Zoom adjusted successfully.")
else:
    print("Failed to adjust zoom.")

# Fast zoom
scroll_to_zoom(1015, speed=10)

# Example for camera(pitch: int, yaw: int, zoom: int, speed=10) -> bool
# Adjusts pitch (0-2047), yaw (0-2047), and final zoom (61-1940). Ensures zoom >=300 during rotation. Uses multiple drag passes from center.
adjusted = camera(pitch=128, yaw=1024, zoom=500, speed=8)
if adjusted:
    print("Camera fully adjusted (pitch, yaw, zoom).")
else:
    print("Camera adjustment failed.")

# North-facing overhead (common for many scripts)
camera(pitch=128, yaw=0, zoom=620)

# High pitch for rooftop agility / safe-spotting
camera(pitch=380, yaw=1536, zoom=300, speed=10)

#---#  
# utils/check_if_in_tile.py
from modules.utils.check_if_in_tile import is_player_idle, check_if_in_tile

# Note: This module checks/moves to specific tiles in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (player), modules.utils.click_minimap_tile, modules.player_data.tile_change, modules.utils.wait_for_tick, math.
# Checks exact tile, moves via minimap if click=True.

# Example for is_player_idle()
# Checks if player is idle (tile stable, animation 0/-1).
idle = is_player_idle()
print(f"Idle: {idle}")

# Example for check_if_in_tile(x, y, plane=0, click=False, right_click=False) -> bool
# Checks if on tile, moves if click=True.
on_tile = check_if_in_tile(2196, 3811, 0, click=True, right_click=True)
print(f"On tile: {on_tile}")

#---#  
# utils/click_minimap_tile.py
from modules.utils.click_minimap_tile import click_minimap_tile

# Note: This module clicks minimap tiles in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.mouse_control, modules.core.plugin_client (minimap_tile_point, player), modules.core.window_utils, random, time.
# Optionally adjusts zoom first, adds random offset, right-clicks.

# Example for click_minimap_tile(target_x, target_y, rand_x=0, rand_y=0, right_click=False, target_zoom: float = None)
# Clicks minimap tile, optionally with zoom adjustment.
clicked = click_minimap_tile(2630, 3123, rand_x=1, rand_y=1, right_click=True, target_zoom=2.0)
print(f"Clicked: {clicked}")

#---#  
# utils/banking.py
from modules.utils.banking import get_all_widget_data, button, get_button_status_and_clickpoints, monitor_button_status, bank, find_items_bank

# Note: This module handles banking interactions in Old School RuneScape via a RuneLite plugin.
# It relies on time, json, random, keyboard, modules.core.plugin_client (_default_client, inventory, bank_items, interact_options, gametick), modules.core.mouse_control (mouse, scroll), modules.core.window_utils (runelite_window).
# Defines bank buttons and shorthands. Main function bank() for deposit/withdraw and button clicks. Scrolls bank view if item not visible.
# find_items_bank() locates and clicks bank items, handling custom amounts with input dialog.

# Example for get_all_widget_data()
# Retrieves all visible widget data as list of dicts.
widgets = get_all_widget_data()
if widgets:
    print(f"Found {len(widgets)} widgets.")
else:
    print("No widget data available.")

# Example for button(button_input)
# Gets (enabled: bool, clickpoint: tuple or None) for bank button by shorthand (e.g., '1', 'noted').
enabled, clickpoint = button("noted")
if enabled:
    print(f"Noted button enabled, clickpoint: {clickpoint}")
else:
    print("Noted button disabled.")

# Example for get_button_status_and_clickpoints() -> dict
# Gets dict of button statuses and clickpoints.
statuses = get_button_status_and_clickpoints()
print(f"Button statuses: {statuses}")

# Example for monitor_button_status()
# Prints status and bounds of bank buttons.
monitor_button_status()

# Example for bank(deposit="", withdraw="", search_button=False, deposit_inventory=False, deposit_equipment=False, placeholder=False, noted=False, unnoted=False, amount=None, quantity=None)
# Performs banking actions: deposit/withdraw items, toggle buttons.
# Returns True if successful.
success = bank(withdraw='prayer potion(4)', quantity="3")
if success:
    print("Withdrew 3 prayer potions.")
else:
    print("Failed.")

# Deposit all
bank(deposit='snapdragon seed', quantity="all")

# Toggle noted and withdraw 1
bank(withdraw='dwarven rock cake', noted=True, quantity="1")

# Deposit 4 with amount
bank(deposit='prayer potion(4)', amount=4)

# Search button
bank(search_button=True)

# Deposit inventory
bank(deposit_inventory=True)

# Placeholder toggle
bank(placeholder=True)

# Example for find_items_bank(item_name, amount=None) -> bool
# Finds, scrolls to, and clicks bank item. Handles custom amount with Withdraw-X.
found = find_items_bank("Dragon bones", amount=10)
if found:
    print("Found and withdrew 10 dragon bones.")
else:
    print("Item not found or click failed.")

#---#  
# utils/check_if_in_area.py
from modules.utils.check_if_in_area import point_in_polygon, is_player_idle, check_if_in_area

# Note: This module checks if the player is in a polygon area defined by tiles in Old School RuneScape via a RuneLite plugin.
# It relies on math, random, modules.core.plugin_client (player, minimap_tiles, walkable_tile), modules.utils.click_minimap_tile, modules.player_data.tile_change, modules.utils.wait_for_tick.
# Uses ray-casting for point-in-polygon. If click=True, moves to random walkable visible tile in area. Waits for idle state.

# Example for point_in_polygon(x, y, vertices) -> bool
# Checks if point (x, y) is inside or on boundary of polygon vertices (list of (x,y) tuples).
inside = point_in_polygon(2202, 3808, [(2201,3812), (2201,3808), (2201,3806), (2203,3806), (2204,3807), (2205,3807), (2205,3812), (2201,3812)])
print(f"Inside: {inside}")

# Example for is_player_idle() -> bool
# Checks if player tile is stable and animation is idle (0 or -1) after one tick.
idle = is_player_idle()
print(f"Player idle: {idle}")

# Example for check_if_in_area(area_tiles, click=False) -> bool
# Checks if player is in area defined by tile strings ["x,y,plane", ...]. If click=True, attempts to move into area.
in_area = check_if_in_area(["2201,3812,0", "2201,3808,0", "2201,3806,0", "2203,3806,0", "2204,3807,0", "2205,3807,0", "2205,3812,0", "2201,3812,0"], click=True)
print(f"In area: {in_area}")

# Alternative area
check_if_in_area(["3214,3221,0", "3214,3211,0", "3227,3211,0", "3227,3226,0", "3217,3226,0", "3214,3221,0"])
#---#
# weapon_data/combat_style.py
from modules.weapon_data.combat_style import load_weapon_data, get_weapon_category, get_style_widget_id, combat_style

# Note: This module switches combat styles in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (gear), modules.core.window_utils, modules.widgets.widget, json, os, pyautogui.
# Loads weapon data from JSON (weapon_data.json). Determines category from equipped weapon, selects style widget.
# Combat tab opened with F3 if needed. Styles: e.g., 'attack', 'strength', 'defence'.

# Example for load_weapon_data()
# Loads weapon data from JSON file. Returns dict or None on error.
data = load_weapon_data()
if data:
    print("Weapon data loaded successfully.")
else:
    print("Failed to load weapon data.")

# Example for get_weapon_category(weapon_name)
# Gets category (e.g., 'blunt') for weapon name (lowercase normalized). Returns str or None.
category = get_weapon_category("dragon dagger")
print(f"Category: {category}")

# Example for get_style_widget_id(category, desired_style)
# Gets widget ID for style in category. Returns int or None.
widget_id = get_style_widget_id("stab", "attack")
print(f"Widget ID: {widget_id}")

# Example for combat_style(desired_style)
# Switches to desired style based on equipped weapon. Returns True if successful or already selected.
success = combat_style('defence')
if success:
    print("Switched to defence style.")
else:
    print("Failed to switch style.")

#---#  
# widgets/widget_data.py
from modules.widgets.widget_data import get_all_widget_data

# Note: This module fetches widget data in Old School RuneScape via a RuneLite plugin.
# It relies on modules.core.plugin_client (_default_client), json.
# Requests all visible widgets and children, returns list of dicts (id, text, etc.) or empty list on error.

# Example for get_all_widget_data()
# Retrieves all visible widget data.
widgets = get_all_widget_data()
if widgets:
    print(f"Found {len(widgets)} widgets.")
else:
    print("No widgets found.")

#---#  
# widgets/widget.py
from modules.widgets.widget import get_widget, check_widget, check_widget_text, check_widget_name, click_widget, click_widget_child, click_widget_by_name

# Note: This module interacts with widgets in Old School RuneScape via a RuneLite plugin.
# It relies on modules.widgets.widget_data, modules.core.mouse_control, modules.core.window_utils, modules.core.plugin_client (interact_options), time, random, re.
# Searches recursively for widgets by id/sprite, checks properties, clicks with options (right-click, action, random offsets).

# Example for get_widget(id_str, sprite_id=None, child_index=None)
# Gets widget dict by ID, optionally with sprite/child. Returns dict or False.
widget = get_widget('8454157', sprite_id=699, child_index=1)
print(f"Widget: {widget}")

# Example for check_widget(id_str, sprite_id=None) -> bool
# Checks if widget exists with matching ID/sprite.
exists = check_widget('8454157', sprite_id=699)
print(f"Exists: {exists}")

# Example for check_widget_text(id_str, child_index=None) -> str or None
# Gets text of widget or child.
text = check_widget_text('8454157', child_index=1)
print(f"Text: {text}")

# Example for check_widget_name(id_str) -> str or None
# Gets name (text) of widget.
name = check_widget_name('8454157')
print(f"Name: {name}")

# Example for click_widget(id_str, sprite_id=None, action=None, right_click=False, sleep_interval=(0,0), clicks=1, rand_x=0, rand_y=0)
# Clicks widget, optionally with action or right-click.
clicked = click_widget('35913778')
print(f"Clicked: {clicked}")

# With action
click_widget('10485782', action='Some Action')

# Multiple clicks
click_widget('8454150', clicks=3, sleep_interval=(0.1, 0.2))

# Example for click_widget_child(id_str, sprite_id=None, child_index=None, action=None, right_click=False, sleep_interval=(0,0), clicks=1, rand_x=0, rand_y=0)
# Clicks child widget.
clicked_child = click_widget_child('8454157', child_index=1)
print(f"Clicked child: {clicked_child}")

# Example for click_widget_by_name(name: str, action=None, right_click=False, sleep_interval=(0,0), clicks=1, rand_x=0, rand_y=0) -> bool
# Clicks widget by name match.
clicked_by_name = click_widget_by_name('Some Widget Name', right_click=True)
print(f"Clicked by name: {clicked_by_name}")

#---#  
# core/plugin_client.py
from modules.core.plugin_client import slayer_task_remaining, varbit_changes, cannon_data, target_npc, fetch_object, players, varbit, quest, stats, gear, chat, npc, inventory, combat_style, inventory_random_clickpoint, game_object, player, tile, walkable_tile, gametick, interact_options, pick, main_menu, bank_items, game_state, get_varbits, get_active_prayers, npc_agro, minimap_tile_point

# print(slayer_task_remaining()) returns: 35
# print(varbit_changes()) returns: {'data': [{'new': 0, 'old': 399, 'tick': 1028, 'varbit': 12391}, {'new': 21, 'old': 20, 'tick': 1028, 'varbit': 12392}, {'new': 409124, 'old': 409123, 'tick': 1028, 'varbit': -1}]}
# print(cannon_data()) returns: {'data': {'ammo': 30, 'exists': True, 'position': 'WorldPoint(x=3195, y=3489, plane=0)', 'id': 6, 'middle_point': {'x': 292, 'y': 223}}}
# print(target_npc()) returns: {'data': {'healthRatio': -1, 'healthScale': -1, 'name': 'Guard', 'index': 19463, 'location': {'plane': 0, 'x': 3208, 'y': 3464}, 'id': 11913, 'middle_point': {'x': 326, 'y': 88}, 'animation': -1}}
# print(fetch_object('1276', 'Chop down', tile_x=3215, tile_y=3452, radius=5, middle_point=True)) returns: {'data': [{'name': 'Tree', 'tile': {'plane': 0, 'x': 3215, 'y': 3452}, 'id': 1276, 'type': 'game_object', 'middle_point': {'x': 474, 'y': 202}, 'on_screen': True}]}
# print(players(radius=10, name="outcastkd")) returns: {'data': [{'healthRatio': -1, 'name': 'OutcastKD', 'location': 'WorldPoint(x=3165, y=3487, plane=0)', 'id': 1328, 'combatLevel': 42, 'isInteracting': False, 'animation': -1}]}
# print(players(radius=1)) returns: {'data': [{'healthRatio': -1, 'name': 'Tha Mush Egg', 'location': 'WorldPoint(x=3164, y=3486, plane=0)', 'id': 1034, 'combatLevel': 96, 'isInteracting': False, 'animation': -1}, {'healthRatio': -1, 'name': 'Prison AP3', 'location': 'WorldPoint(x=3164, y=3486, plane=0)', 'id': 1691, 'combatLevel': 27, 'isInteracting': False, 'animation': -1}]}
# print(varbit(varbit_id=12391)) # returns: 475
# print(quest()) returns: {'data': {'Dream Mentor': 'NOT_STARTED', 'Fairytale I - Growing Pains': 'NOT_STARTED', 'The Golem': 'NOT_STARTED', 'Recipe for Disaster - Pirate Pete': 'NOT_STARTED', 'The Fremennik Exiles': 'NOT_STARTED', 'Misthalin Mystery': 'NOT_STARTED', 'The Enchanted Key': 'NOT_STARTED', "Witch's House": 'FINISHED', 'Family Pest': 'NOT_STARTED', 'Desert Treasure II - The Fallen Empire': 'NOT_STARTED', 'Dwarf Cannon': 'FINISHED', 'Garden of Tranquillity': 'NOT_STARTED', 'Horror from the Deep': 'NOT_STARTED'}}
# print(stats()) returns: {'data': {'Hunter': {'level': 1, 'xp': 0}, 'Thieving': {'level': 14, 'xp': 2175}, 'Runecraft': {'level': 1, 'xp': 0}, 'Construction': {'level': 1, 'xp': 0}, 'Cooking': {'level': 1, 'xp': 70}, 'Magic': {'level': 62, 'xp': 357964}, 'Fletching': {'level': 10, 'xp': 1180}, 'Herblore': {'level': 1, 'xp': 0}, 'Firemaking': {'level': 1, 'xp': 40}, 'Attack': {'level': 44, 'xp': 55783}, 'Fishing': {'level': 1, 'xp': 10}, 'Crafting': {'level': 7, 'xp': 750}, 'Hitpoints': {'level': 38, 'xp': 30756}, 'Ranged': {'level': 35, 'xp': 24226}, 'Mining': {'level': 10, 'xp': 1352}, 'Sailing': {'level': 1, 'xp': 0}, 'Smithing': {'level': 29, 'xp': 12743}, 'Agility': {'level': 66, 'xp': 496573}, 'Woodcutting': {'level': 1, 'xp': 25}, 'Slayer': {'level': 33, 'xp': 18499}, 'Defence': {'level': 32, 'xp': 16675}, 'Strength': {'level': 30, 'xp': 13984}, 'Prayer': {'level': 82, 'xp': 2499230}, 'Farming': {'level': 1, 'xp': 0}}}
# print(gear()) returns: {'data': {'Graceful cape': 11853, 'Graceful legs': 11857, 'Graceful hood': 11851, 'Ring of wealth (4)': 11982, 'Graceful top': 11855, 'Amulet of glory(6)': 11978, 'Graceful gloves': 11859, 'Graceful boots': 11861}}
# print(chat()) returns: {'data': ['upseeripasi:', 'Lol', 'Did you know? Eating a strange fruit cures poison and venom as well as restoring run energy.', 'Birinol:', '                                                                                ', 'Welcome to Old School RuneScape.']}
# # npc(id: str = "", name: str = "", tile: bool = True, middle_point: bool = True,
# #         animation: bool = True, size: bool = True, in_combat: Optional[bool] = None) -> Optional[Dict[str, Any]]:
# print(npc(name="Banker")) returns: {'data': [{'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3163, 'y': 3489}, 'id': 1633, 'middle_point': {'x': 423, 'y': 146}, 'animation': -1}, {'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3166, 'y': 3489}, 'id': 1634, 'middle_point': {'x': 322, 'y': 287}, 'animation': -1}, {'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3166, 'y': 3490}, 'id': 3089, 'middle_point': {'x': 370, 'y': 322}, 'animation': -1}]}
# print(npc()) returns: {'data': [{'size': 1, 'name': 'Relobo Blinyo (logs)', 'tile': {'plane': 0, 'x': 3152, 'y': 3489}, 'id': 5451, 'middle_point': {'x': -235, 'y': 98}, 'animation': -1}, {'size': 1, 'name': 'Bob Barter (herbs)', 'tile': {'plane': 0, 'x': 3156, 'y': 3481}, 'id': 5449, 'middle_point': {'x': -168, 'y': 434}, 'animation': -1}, {'size': 1, 'name': 'Hofuthand (weapons and armour)', 'tile': {'plane': 0, 'x': 3156, 'y': 3498}, 'id': 5452, 'middle_point': {'x': -17, 'y': -144}, 'animation': -1}, {'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3163, 'y': 3489}, 'id': 1633, 'middle_point': {'x': 184, 'y': 98}, 'animation': -1}, {'size': 1, 'name': 'null', 'tile': {'plane': 0, 'x': 3163, 'y': 3490}, 'id': 1613, 'middle_point': {'x': 186, 'y': 65}, 'animation': -1}, {'size': 1, 'name': 'Grand Exchange Clerk', 'tile': {'plane': 0, 'x': 3164, 'y': 3488}, 'id': 2149, 'middle_point': {'x': 221, 'y': 132}, 'animation': -1}, {'size': 1, 'name': 'Grand Exchange Clerk', 'tile': {'plane': 0, 'x': 3164, 'y': 3491}, 'id': 2151, 'middle_point': {'x': 224, 'y': 34}, 'animation': -1}, {'size': 1, 'name': 'Brugsen Bursen', 'tile': {'plane': 0, 'x': 3165, 'y': 3477}, 'id': 2152, 'middle_point': {'x': 260, 'y': 674}, 'animation': -1}, {'size': 1, 'name': 'Grand Exchange Clerk', 'tile': {'plane': 0, 'x': 3165, 'y': 3488}, 'id': 2148, 'middle_point': {'x': 260, 'y': 132}, 'animation': -1}, {'size': 1, 'name': 'Grand Exchange Clerk', 'tile': {'plane': 0, 'x': 3165, 'y': 3491}, 'id': 2150, 'middle_point': {'x': 260, 'y': 34}, 'animation': -1}, {'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3166, 'y': 3489}, 'id': 1634, 'middle_point': {'x': 298, 'y': 98}, 'animation': -1}, {'size': 1, 'name': 'Banker', 'tile': {'plane': 0, 'x': 3166, 'y': 3490}, 'id': 3089, 'middle_point': {'x': 297, 'y': 65}, 'animation': -1}, {'size': 1, 'name': 'Murky Matt (runes)', 'tile': {'plane': 0, 'x': 3173, 'y': 3481}, 'id': 5450, 'middle_point': {'x': 641, 'y': 434}, 'animation': -1}, {'size': 1, 'name': 'Farid Morrisane (ores and bars)', 'tile': {'plane': 0, 'x': 3173, 'y': 3498}, 'id': 3115, 'middle_point': {'x': 506, 'y': -144}, 'animation': -1}]}
# print(inventory("cannonball")) returns: {'data': [{'random_clickpoint': {'x': 578, 'y': 256}, 'name': 'Steel cannonball', 'id': 2, 'middle_point': {'x': 588, 'y': 265}}]}
# print(inventory()) returns: {'data': [{'random_clickpoint': {'x': 593, 'y': 215}, 'name': 'Cannon base', 'id': 6, 'middle_point': {'x': 588, 'y': 229}}, {'random_clickpoint': {'x': 639, 'y': 242}, 'name': 'Cannon stand', 'id': 8, 'middle_point': {'x': 630, 'y': 229}}, {'random_clickpoint': {'x': 659, 'y': 227}, 'name': 'Cannon barrels', 'id': 10, 'middle_point': {'x': 672, 'y': 229}}, {'random_clickpoint': {'x': 728, 'y': 240}, 'name': 'Cannon furnace', 'id': 12, 'middle_point': {'x': 714, 'y': 229}}, {'random_clickpoint': {'x': 602, 'y': 267}, 'name': 'Steel cannonball', 'id': 2, 'middle_point': {'x': 588, 'y': 265}}]}
# print(combat_style()) returns: {'data': {'style': 'Unknown', 'category': 'Unknown'}} OR {'data': {'style': 'Strength', 'category': 'Slash Sword'}}
# print(inventory_random_clickpoint()) returns: {'data': [{'random_clickpoint': {'x': 599, 'y': 231}, 'name': 'Cannon base', 'id': 6, 'middle_point': {'x': 588, 'y': 229}}, {'random_clickpoint': {'x': 631, 'y': 236}, 'name': 'Cannon stand', 'id': 8, 'middle_point': {'x': 630, 'y': 229}}, {'random_clickpoint': {'x': 681, 'y': 238}, 'name': 'Cannon barrels', 'id': 10, 'middle_point': {'x': 672, 'y': 229}}, {'random_clickpoint': {'x': 724, 'y': 232}, 'name': 'Cannon furnace', 'id': 12, 'middle_point': {'x': 714, 'y': 229}}, {'random_clickpoint': {'x': 599, 'y': 275}, 'name': 'Steel cannonball', 'id': 2, 'middle_point': {'x': 588, 'y': 265}}]}
# # def game_object(object: str = "", tile: bool = True, tile_radius: int = 6,
# #                 middle_point: bool = True) -> Optional[Dict[str, Any]]:
# print(game_object()) returns: {'data': [{'name': 'null', 'tile': {'plane': 0, 'x': 3159, 'y': 3481}, 'id': 10653, 'middle_point': {'x': -28, 'y': -238}}, {'name': "Forester's Campfire", 'tile': {'plane': 0, 'x': 3161, 'y': 3489}, 'id': 49927, 'middle_point': {'x': 416, 'y': -17}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3163, 'y': 3488}, 'id': 10059, 'middle_point': {'x': 342, 'y': 72}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3163, 'y': 3491}, 'id': 10059, 'middle_point': {'x': 514, 'y': 110}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3164, 'y': 3489}, 'id': 10063, 'middle_point': {'x': 416, 'y': 170}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3164, 'y': 3489}, 'id': 10063, 'middle_point': {'x': 416, 'y': 170}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3164, 'y': 3489}, 'id': 10063, 'middle_point': {'x': 416, 'y': 170}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3164, 'y': 3489}, 'id': 10063, 'middle_point': {'x': 416, 'y': 170}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3166, 'y': 3488}, 'id': 10062, 'middle_point': {'x': 305, 'y': 241}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3166, 'y': 3491}, 'id': 10059, 'middle_point': {'x': 480, 'y': 282}}, {'name': "Forester's Campfire", 'tile': {'plane': 0, 'x': 3168, 'y': 3489}, 'id': 49927, 'middle_point': {'x': 336, 'y': 372}}, {'name': 'null', 'tile': {'plane': 0, 'x': 3170, 'y': 3481}, 'id': 10651, 'middle_point': {'x': -207, 'y': 371}}]}
# # def player(location: bool = True, health: bool = True, prayer: bool = True, run: bool = True,
# #            weight: bool = True, animation: bool = True, camera: bool = True) -> Optional[Dict[str, Any]]:
# print(player()) returns: {'data': {'prayer': 28, 'health': 38, 'weight': 7, 'location': {'plane': 0, 'x': 3165, 'y': 3487}, 'camera': {'zoom': 928, 'pitch': 465, 'yaw': 584}, 'runEnergy': 100, 'animation': -1}}
# # def tile(tile_x: int = 0, tile_y: int = 0, tile_radius: int = 6,
# #          middle_point: bool = True) -> Optional[Dict[str, Any]]:
# print(tile(tile_radius=1)) returns: {'data': [{'plane': 0, 'x': 3164, 'y': 3486, 'middle_point': {'x': 218, 'y': 111}}, {'plane': 0, 'x': 3164, 'y': 3487, 'middle_point': {'x': 272, 'y': 123}}, {'plane': 0, 'x': 3164, 'y': 3488, 'middle_point': {'x': 327, 'y': 135}}, {'plane': 0, 'x': 3165, 'y': 3486, 'middle_point': {'x': 205, 'y': 165}}, {'plane': 0, 'x': 3165, 'y': 3487, 'middle_point': {'x': 260, 'y': 177}}, {'plane': 0, 'x': 3165, 'y': 3488, 'middle_point': {'x': 315, 'y': 189}}, {'plane': 0, 'x': 3166, 'y': 3486, 'middle_point': {'x': 192, 'y': 220}}, {'plane': 0, 'x': 3166, 'y': 3487, 'middle_point': {'x': 248, 'y': 232}}, {'plane': 0, 'x': 3166, 'y': 3488, 'middle_point': {'x': 303, 'y': 245}}]}
# # def walkable_tile(tile_x: int = 0, tile_y: int = 0, tile_radius: int = 0,
# #                   middle_point: bool = True) -> Optional[Dict[str, Any]]:
# print(walkable_tile(tile_radius=2)) returns: {'data': [{'plane': 0, 'x': 3164, 'y': 3485, 'middle_point': {'x': 164, 'y': 99}}, {'plane': 0, 'x': 3167, 'y': 3487, 'middle_point': {'x': 235, 'y': 288}}, {'plane': 0, 'x': 3167, 'y': 3488, 'middle_point': {'x': 291, 'y': 301}}, {'plane': 0, 'x': 3163, 'y': 3487, 'middle_point': {'x': 284, 'y': 70}}, {'plane': 0, 'x': 3164, 'y': 3486, 'middle_point': {'x': 218, 'y': 111}}, {'plane': 0, 'x': 3165, 'y': 3485, 'middle_point': {'x': 150, 'y': 153}}, {'plane': 0, 'x': 3164, 'y': 3487, 'middle_point': {'x': 272, 'y': 123}}, {'plane': 0, 'x': 3167, 'y': 3489, 'middle_point': {'x': 348, 'y': 314}}, {'plane': 0, 'x': 3165, 'y': 3486, 'middle_point': {'x': 205, 'y': 165}}, {'plane': 0, 'x': 3166, 'y': 3485, 'middle_point': {'x': 137, 'y': 207}}, {'plane': 0, 'x': 3165, 'y': 3487, 'middle_point': {'x': 260, 'y': 177}}, {'plane': 0, 'x': 3166, 'y': 3486, 'middle_point': {'x': 192, 'y': 220}}, {'plane': 0, 'x': 3167, 'y': 3485, 'middle_point': {'x': 123, 'y': 263}}, {'plane': 0, 'x': 3166, 'y': 3487, 'middle_point': {'x': 248, 'y': 232}}, {'plane': 0, 'x': 3167, 'y': 3486, 'middle_point': {'x': 179, 'y': 276}}, {'plane': 0, 'x': 3163, 'y': 3485, 'middle_point': {'x': 177, 'y': 46}}, {'plane': 0, 'x': 3163, 'y': 3486, 'middle_point': {'x': 231, 'y': 58}}]}
# print(gametick()) returns: {'data': 4025}
# print(interact_options()) returns: {'data': [{'middle_point': {'x': 314, 'y': 206}, 'option': 'Exchange', 'target': '<col=ffff00>Grand Exchange Clerk'}, {'middle_point': {'x': 314, 'y': 221}, 'option': 'Talk-to', 'target': '<col=ffff00>Grand Exchange Clerk'}, {'middle_point': {'x': 314, 'y': 235}, 'option': 'History', 'target': '<col=ffff00>Grand Exchange Clerk'}, {'middle_point': {'x': 314, 'y': 250}, 'option': 'Sets', 'target': '<col=ffff00>Grand Exchange Clerk'}, {'middle_point': {'x': 314, 'y': 266}, 'option': 'Walk here', 'target': ''}, {'middle_point': {'x': 314, 'y': 282}, 'option': 'Examine', 'target': '<col=ffff00>Grand Exchange Clerk'}, {'middle_point': {'x': 314, 'y': 297}, 'option': 'Cancel', 'target': ''}]}
# # def pick(x: int, y: int, size: int = 0, item: str = "") -> Optional[Dict[str, Any]]:
# print(pick(x=3165, y=3487, size=5)) returns: {'data': {'item': '', 'function': 'pick', 'items': [{'name': 'Waterskin(0)', 'tile': {'plane': 0, 'x': 3162, 'y': 3488}, 'id': 1831, 'middle_point': {'x': 186, 'y': 13}}, {'name': 'Cannon base', 'tile': {'plane': 0, 'x': 3165, 'y': 3487}, 'id': 6, 'middle_point': {'x': 261, 'y': 257}}, {'name': 'Vial', 'tile': {'plane': 0, 'x': 3166, 'y': 3487}, 'id': 229, 'middle_point': {'x': 332, 'y': 344}}]}}
# print(main_menu()) returns: {'data': 'LOGIN_SCREEN'}
# print(bank_items()) returns: {'data': [{'random_clickpoint': {'x': 85, 'y': -199}, 'quantity': 1, 'name': 'Bronze axe', 'id': 1351, 'middle_point': {'x': 91, 'y': -199}}, {'random_clickpoint': {'x': 123, 'y': -196}, 'quantity': 1, 'name': 'Bronze pickaxe', 'id': 1265, 'middle_point': {'x': 139, 'y': -199}}, {'random_clickpoint': {'x': 175, 'y': -208}, 'quantity': 1, 'name': 'Tinderbox', 'id': 590, 'middle_point': {'x': 187, 'y': -199}}, {'random_clickpoint': {'x': 182, 'y': 114}, 'quantity': 0, 'name': 'Cannon base', 'id': 17857, 'middle_point': {'x': 187, 'y': 125}}, {'random_clickpoint': {'x': 248, 'y': 138}, 'quantity': 0, 'name': 'Graceful top', 'id': 18210, 'middle_point': {'x': 235, 'y': 125}}, {'random_clickpoint': {'x': 275, 'y': 128}, 'quantity': 0, 'name': 'Graceful legs', 'id': 18211, 'middle_point': {'x': 283, 'y': 125}}, {'random_clickpoint': {'x': 335, 'y': 116}, 'quantity': 0, 'name': 'Cannon stand', 'id': 17858, 'middle_point': {'x': 331, 'y': 125}}, {'random_clickpoint': {'x': 382, 'y': 134}, 'quantity': 0, 'name': 'Cannon barrels', 'id': 17859, 'middle_point': {'x': 379, 'y': 125}}, {'random_clickpoint': {'x': 439, 'y': 118}, 'quantity': 0, 'name': 'Cannon furnace', 'id': 17860, 'middle_point': {'x': 427, 'y': 125}}, {'random_clickpoint': {'x': 75, 'y': 162}, 'quantity': 1, 'name': 'Rune scimitar', 'id': 1333, 'middle_point': {'x': 91, 'y': 161}}, {'random_clickpoint': {'x': 147, 'y': 155}, 'quantity': 1, 'name': 'Stamina potion(3)', 'id': 12627, 'middle_point': {'x': 139, 'y': 161}}, {'random_clickpoint': {'x': 202, 'y': 156}, 'quantity': 8, 'name': 'Vial', 'id': 229, 'middle_point': {'x': 187, 'y': 161}}, {'random_clickpoint': {'x': 228, 'y': 167}, 'quantity': 0, 'name': 'Pure essence', 'id': 19226, 'middle_point': {'x': 235, 'y': 161}}, {'random_clickpoint': {'x': 284, 'y': 156}, 'quantity': 0, 'name': 'Prayer potion(2)', 'id': 19330, 'middle_point': {'x': 283, 'y': 161}}, {'random_clickpoint': {'x': 317, 'y': 162}, 'quantity': 0, 'name': 'Graceful hood', 'id': 18208, 'middle_point': {'x': 331, 'y': 161}}, {'random_clickpoint': {'x': 380, 'y': 169}, 'quantity': 1, 'name': 'Antidote++(2)', 'id': 5956, 'middle_point': {'x': 379, 'y': 161}}, {'random_clickpoint': {'x': 418, 'y': 174}, 'quantity': 1, 'name': 'Prayer potion(3)', 'id': 139, 'middle_point': {'x': 427, 'y': 161}}, {'random_clickpoint': {'x': 105, 'y': 201}, 'quantity': 1, 'name': 'Prayer potion(1)', 'id': 143, 'middle_point': {'x': 91, 'y': 197}}, {'random_clickpoint': {'x': 123, 'y': 207}, 'quantity': 1, 'name': 'Earmuffs', 'id': 4166, 'middle_point': {'x': 139, 'y': 197}}, {'random_clickpoint': {'x': 176, 'y': 210}, 'quantity': 10, 'name': 'Waterskin(4)', 'id': 1823, 'middle_point': {'x': 187, 'y': 197}}, {'random_clickpoint': {'x': 250, 'y': 187}, 'quantity': 1, 'name': 'Waterskin(3)', 'id': 1825, 'middle_point': {'x': 235, 'y': 197}}, {'random_clickpoint': {'x': 297, 'y': 204}, 'quantity': 218, 'name': 'Ice cooler', 'id': 6696, 'middle_point': {'x': 283, 'y': 197}}, {'random_clickpoint': {'x': 331, 'y': 205}, 'quantity': 27, 'name': "Fenkenstrain's castle teleport", 'id': 19621, 'middle_point': {'x': 331, 'y': 197}}, {'random_clickpoint': {'x': 372, 'y': 196}, 'quantity': 1, 'name': 'Enchanted gem', 'id': 4155, 'middle_point': {'x': 379, 'y': 197}}, {'random_clickpoint': {'x': 322, 'y': 275}, 'quantity': 40, 'name': 'Mithril seeds', 'id': 299, 'middle_point': {'x': 331, 'y': 269}}, {'random_clickpoint': {'x': 389, 'y': 274}, 'quantity': 1, 'name': 'Ring of wealth (3)', 'id': 11984, 'middle_point': {'x': 379, 'y': 269}}]}
# print(game_state()) returns: {'data': 'LOGGED_IN'}
# print(get_varbits(varbit_ids=[12391, 4567, 8901])) returns: {'data': {'values': {'12391': 69, '8901': 0, '4567': 0}}}
# print(get_active_prayers()) returns: {'data': {'STEEL_SKIN': False, 'RP_UMBRA_VOW': False, 'RP_ANCIENT_STRENGTH': False, 'ROCK_SKIN': False, 'RP_CRUORS_VOW': False, 'RP_METABOLISE': False, 'EAGLE_EYE': False, 'CLARITY_OF_THOUGHT': False, 'RP_GLACIES_VOW': False, 'RP_FUMUS_VOW': False, 'RP_TRINITAS': False, 'RP_DAMPEN_RANGED': False, 'CHIVALRY': False, 'SUPERHUMAN_STRENGTH': False, 'MYSTIC_VIGOUR': False, 'RP_VAPORISE': False, 'BURST_OF_STRENGTH': False, 'PROTECT_FROM_MISSILES': False, 'PROTECT_ITEM': False, 'RIGOUR': False, 'RP_BERSERKER': False, 'MYSTIC_MIGHT': False, 'DEADEYE': False, 'RP_ANCIENT_WILL': False, 'PROTECT_FROM_MAGIC': False, 'RAPID_HEAL': True, 'RP_DAMPEN_MELEE': False, 'RP_VINDICATION': False, 'PRESERVE': False, 'RP_PROTECT_ITEM': False, 'IMPROVED_REFLEXES': False, 'RP_RUINOUS_GRACE': False, 'RP_ANNIHILATE': False, 'THICK_SKIN': False, 'HAWK_EYE': False, 'AUGURY': False, 'RP_REBUKE': False, 'SMITE': False, 'RP_INTENSIFY': False, 'INCREDIBLE_REFLEXES': False, 'RETRIBUTION': False, 'REDEMPTION': False, 'RAPID_RESTORE': False, 'SHARP_EYE': False, 'RP_WRATH': False, 'RP_ANCIENT_SIGHT': False, 'RP_REJUVENATION': False, 'MYSTIC_WILL': False, 'MYSTIC_LORE': False, 'ULTIMATE_STRENGTH': False, 'RP_PURGE': False, 'PIETY': False, 'RP_DAMPEN_MAGIC': False, 'RP_DECIMATE': False, 'PROTECT_FROM_MELEE': False}}
# print(npc_agro()) returns: Aggressive NPCs: - Guard (ID: 11911): Status: green, Can Reach: True, On Cooldown: False, Cooldown Remaining: 0 ticks {'aggressiveNpcs': [{'onCooldown': False, 'attackSpeed': 4, 'name': 'Guard', 'health': 28, 'location': 'WorldPoint(x=3212, y=3457, plane=0)', 'cooldownRemaining': 0, 'id': 11911, 'canReach': True}]}
# print(minimap_tile_point(tile_x=3213, tile_y=3456))  # returns: {'data': {'x': 641, 'y': 81, 'zoom': 2.0}}

#---#  
# scripts/combat/slayer/slayer_master_edgeville.py
# A script for navigating to the Slayer Master Vannaka in Edgeville Dungeon in Old School RuneScape via RuneLite plugin.
from scripts.combat.slayer.slayer_master_edgeville import full_navigation
full_navigation()

from modules.utils.monitor_clicks import monitor_clicks returns: 
# Click #1:
#   Tick: 27
#   Type: menu_option
#   Option: Open
#   Target: Gate
#   Canvas Position: (255, 114)
#   Entity Type: object-
#     Object Name: Gate
#     Object ID: 1728
#     Object Tile: (3132, 9864, plane: 0)

# Click #2:
#   Tick: 31
#   Type: menu_option
#   Option: Don't go
#   Target: 
#   Canvas Position: (343, 257)

# Click #3:
#   Tick: 36
#   Type: menu_option
#   Option: Set-up
#   Target: Cannon base
#   Canvas Position: (588, 232)

# Click #4:
#   Tick: 49
#   Type: menu_option
#   Option: Worn Equipment
#   Target: 
#   Canvas Position: (679, 191)
#   Widget Changes:
#     Widget ID: 35913795, Path: _1_9_1_3, Old Sprite: 1030, New Sprite: -1

# Click #5:
#   Tick: 51
#   Type: menu_option
#   Option: View equipment stats
#   Target: 
#   Canvas Position: (584, 427)

# Click #6:
#   Tick: 57
#   Type: menu_option
#   Option: Close
#   Target: 
#   Canvas Position: (492, 24)

# Click #7:
#   Tick: 65
#   Type: menu_option
#   Option: Cancel
#   Target: 
#   Canvas Position: (641, 110)
#   Minimap Click: True
#   Minimap Tile: (3131, 9911, plane: 0)

# Click #8:
#   Tick: 71
#   Type: menu_option
#   Option: Walk here
#   Target: 
#   Canvas Position: (307, 178)
#   Clicked Tile: (3383, 9864, plane: 0)

# Click #9:
#   Tick: 83
#   Type: menu_option
#   Option: Remove
#   Target: Brine sabre
#   Canvas Position: (590, 306)
#   Widget Changes:
#     Widget ID: 10485798, Path: _1_2_7_0_5_3, Old Sprite: 1607, New Sprite: 1064

# Click #10:
#   Tick: 93
#   Type: menu_option
#   Option: Activate
#   Target: Quick-prayers
#   Canvas Position: (545, 91)
#   Widget Changes:
#     Widget ID: 10485782, Path: _1_2_7_0_3_3, Old Sprite: 1063, New Sprite: 1066
#     Widget ID: 10485785, Path: _1_2_7_0_3_5, Old Sprite: 1068, New Sprite: 1058