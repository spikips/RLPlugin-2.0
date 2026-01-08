import time, re, random, math
from modules.core.plugin_client import player, minimap_tiles, walkable_tile, gear, players, game_state, pick, gametick, npc
from modules.utils.click_minimap_tile import click_minimap_tile
from modules.player_data.tile_change import wait_for_tile_change
from modules.player_data.wait_till_character_stops_moving import wait_till_character_stopped_moving
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
from modules.object_data.game_object import click_gameobject, get_closest_game_object, get_game_objects, hover_gameobject
from modules.core.plugin_client import fetch_object
from modules.object_data.object import click_object, check_object, get_closest_object, use_on_object
from modules.core.mouse_control import move
from modules.widgets.widget_data import get_all_widget_data
from modules.core.window_utils import runelite_window, focus_runelite_window
from modules.player_data.prayer.toggle_prayer import toggle_prayer




def swamp_tree_room():
    def continue_trek():
        click_object('13832', 'continue-trek')
        return True

    def handle_swamp_tree_branch():
        pl_data = player(location=True)
        initial_loc = pl_data['data']['location']
        initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
        click_gameobject('13846', 'swing-from')
        for _ in range(10):
            wait_for_tick()
            pl_data = player(location=True)
            current_loc = pl_data['data']['location']
            current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
            print(f"Current Tile: {current_tile}, Initial Tile: {initial_tile}")
            if current_tile[1] > initial_tile[1] + 4:
                wait_for_tick(10)
                return True
        
    def use_long_vine_on_swamp_tree_branch():
        click_inventory('long vine', 'use')
        click_gameobject('13845', 'Use Long vine -> Swamp tree branch')
        while True:
            swamp_tree_branch = get_closest_game_object('13846', None, 10)
            if swamp_tree_branch:
                return True
        

    def cut_short_vines():
        vine_ids = ['13847', '13848', '13849']  # List of all possible vine IDs to try
        while get_inventory_count('short vine') < 3:
            increased = False
            for vine_id in vine_ids:
                old_count = get_inventory_count('short vine')
                click_vine = click_gameobject(vine_id, 'Cut-vine')
                if not click_vine:
                    continue  # Try next vine ID if click failed
                
                # Wait to see if count changed (with timeout to avoid infinite loop)
                for _ in range(40):
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

        click_inventory_sequence(['short vine', 'short vine'])
        wait_for_tick(3)
        return True

    swamp_tree_branch = get_closest_game_object('13846', None, 10)
    if swamp_tree_branch:
        if handle_swamp_tree_branch():
            if continue_trek():
                return True
        
    if get_inventory_count('long vine') > 0:
        if use_long_vine_on_swamp_tree_branch():
            if handle_swamp_tree_branch():
                if continue_trek():
                    return True

    if cut_short_vines():
        if get_inventory_count('long vine') > 0:
            if use_long_vine_on_swamp_tree_branch():
                if handle_swamp_tree_branch():
                    if continue_trek():
                        return True

def zombie_room():
    def go_to_broken_bridge():
        bridge_tile = broken_bridge['tile']
        if broken_bridge:
            bridge_tile = broken_bridge['tile']
            target_x = bridge_tile['x']
            target_y = bridge_tile['y'] - 1
            target_plane = bridge_tile['plane']
            target_tile = (target_x, target_y, target_plane)
            print(f"Clicking on target tile y-1: {target_tile}")
            click_minimap_tile(*target_tile, target_zoom=5)
            wait_till_character_stopped_moving()  # Optional: wait for arrival
        else:
            print("No broken bridge found.")

    go_to_broken_bridge()
    exit()

def dead_tree_room():
    def continue_trek():
        click_object('13832', 'continue-trek')
        return True

    def use_logs_on_broken_bridge():
        """
        Repairs the broken bridge using logs, starting from any state, until fully fixed and crossed.
        - States: Broken (13834) -> Partially (13835) -> Slightly (13836) -> Fixed (13837).
        - Automatically detects current state and progresses.
        """
        # Define bridge states as a list of (obj_id, repair_action, use_option, next_id)
        # For fixed, no repair needed, just cross
        states = [
            (13834, 'Inspect', 'use logs -> broken bridge', 13835),
            (13835, 'Inspect', 'use logs -> Partially broken bridge', 13836),
            (13836, 'Inspect', 'use logs -> Slightly broken bridge', 13837),
        ]
        fixed_id = 13837
        cross_action = 'Cross'

        current_state_id = None
        for state_id, _, _, _ in states + [(fixed_id, None, None, None)]:
            if get_closest_object(str(state_id), 'Inspect' if state_id != fixed_id else cross_action):
                current_state_id = state_id
                break

        if current_state_id is None:
            print("No bridge state detected nearby.")
            return False

        # If already fixed, just cross
        if current_state_id == fixed_id:
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True

        # Progress through repair states
        for state_id, repair_action, use_option, next_id in states:
            if current_state_id != state_id:
                continue

            # Use logs and repair current state
            click_inventory('logs', 'use')
            use_on_object(str(state_id), repair_action, use_option)

            # Wait until next state appears (or fixed)
            while not get_closest_object(str(next_id), 'Inspect' if next_id != fixed_id else cross_action):
                wait_for_tick()

            current_state_id = next_id
            if current_state_id == fixed_id:
                break

        # Cross the fixed bridge
        if get_closest_object(str(fixed_id), cross_action):
            click_object(str(fixed_id), cross_action)
            wait_till_character_stopped_moving()
            wait_for_tick(2)
            return True

        return False

    def go_to_broken_bridge():
        bridge_tile = broken_bridge['tile']
        if broken_bridge:
            bridge_tile = broken_bridge['tile']
            target_x = bridge_tile['x']
            target_y = bridge_tile['y'] - 1
            target_plane = bridge_tile['plane']
            target_tile = (target_x, target_y, target_plane)
            print(f"Clicking on target tile y-1: {target_tile}")
            click_minimap_tile(*target_tile, target_zoom=5)
            wait_till_character_stopped_moving()
            return True
        else:
            print("No broken bridge found.")
    
    def cut_dead_trees(target_logs=3, max_click_attempts=3, wait_ticks=30, search_distance=10):
        """
        Chops down dead trees to collect up to target_logs in inventory.
        
        Args:
            target_logs: Maximum number of logs to collect.
            max_click_attempts: Number of click attempts per chop cycle.
            wait_ticks: Ticks to wait and check for logs after each click.
            search_distance: Distance to search for the closest dead tree.
        """
        current_logs = get_inventory_count('logs')
        if current_logs >= target_logs:
            return  True

        dead_tree = get_closest_game_object('1365', None, search_distance)
        if not dead_tree:
            return  # No tree nearby

        while current_logs < target_logs:
            progress_made = False
            for _ in range(max_click_attempts):
                click_gameobject('1365', 'chop down')
                for _ in range(wait_ticks):
                    wait_for_tick()
                    new_logs = get_inventory_count('logs')
                    if new_logs > current_logs:
                        current_logs = new_logs
                        progress_made = True
                        break  # Log obtained, no need to wait further
                if progress_made:
                    break  # Successfully chopped once, check outer condition
            if not progress_made:
                break  # No progress (e.g., tree depleted), stop trying
        
        return True

    # if not get_closest_object('13837', 'Cross'):
    #     if get_inventory_count('logs') == 3:
    #         if go_to_broken_bridge():
    #             if use_logs_on_broken_bridge():
    #                 evade_event()
    #                 return True
    # else:
    #     evade_event()


    if cut_dead_trees():
        if go_to_broken_bridge():
            if use_logs_on_broken_bridge():
                continue_trek()
                return True



def evade_event():
    click_object('13831', 'Evade-event')
    wait_till_character_stopped_moving()
    wait_for_tile_change()
    wait_for_tick(2)


while True:
    broken_bridge = get_closest_object('13834', 'Inspect')
    print(f"Broken Bridge Found: {broken_bridge}")
    if broken_bridge:
        # check for tree
        check_dead_tree = get_closest_game_object('1365', None, 10)
        if check_dead_tree:
            print("Dead tree found, entering dead tree room")
            dead_tree_room()
        else:
            print("No dead tree found, entering zombie room")
            zombie_room()

    check_swamp_tree = get_closest_game_object('13843', None, 10)
    if check_swamp_tree:
        swamp_tree_room()

    riyl_shadow = npc(name='riyl shadow')
    if riyl_shadow:
        evade_event()


    nail_beast = npc(name='nail beast')
    if nail_beast:
        evade_event()

    swamp_snake = npc(name='swamp snake')
    if swamp_snake:
        evade_event()

    giant_snail = npc(name='giant snail')
    if giant_snail:
        evade_event()

    vampyre_juvinate = npc(name='vampyre juvinate')
    if vampyre_juvinate:
        evade_event()

    ghast = npc(name='ghast')
    if ghast:
        evade_event()




