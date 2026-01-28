# monitor_clicks.py
# This file provides standalone functions to interact with the ClickHandler via the plugin server.
# It uses the _default_client from plugin_client.py to send requests and print click data.

from typing import Optional, Dict, List, Any

from modules.core.plugin_client import player
from modules.utils.wait_for_tick import wait_for_next_tick
from modules.core.plugin_client import player, gametick
from modules.core.plugin_client import _default_client

def _print_click_data(click_data: Dict[str, Any], print_text: bool = True, max_changes: Optional[int] = None):
    """
    Helper function to format and print click data, including tick and any changes.
    
    Args:
        click_data (Dict[str, Any]): The click data to print.
        print_text (bool): Whether to print text-related widget changes (default: True).
        max_changes (Optional[int]): Maximum number of sprite-related widget changes to print (default: None, meaning all). Text changes are always printed in full if print_text=True.
    """
    print(f"  Tick: {click_data.get('tick', 'N/A')}")
    print(f"  Type: {click_data.get('type', 'N/A')}")
    if 'option' in click_data:
        print(f"  Option: {click_data.get('option', 'N/A')}")
    if 'target' in click_data:
        print(f"  Target: {click_data.get('target', 'N/A')}")
    if 'canvas_pos' in click_data:
        pos = click_data['canvas_pos']
        print(f"  Canvas Position: ({pos.get('x', 'N/A')}, {pos.get('y', 'N/A')})")
    if 'is_minimap_click' in click_data:
        print(f"  Minimap Click: {click_data['is_minimap_click']}")
        if 'minimap_tile' in click_data:
            tile = click_data['minimap_tile']
            print(f"  Minimap Tile: ({tile.get('x', 'N/A')}, {tile.get('y', 'N/A')}, plane: {tile.get('plane', 'N/A')})")
    if 'clicked_tile' in click_data:
        tile = click_data['clicked_tile']
        print(f"  Clicked Tile: ({tile.get('x', 'N/A')}, {tile.get('y', 'N/A')}, plane: {tile.get('plane', 'N/A')})")
    if 'entity_type' in click_data:
        print(f"  Entity Type: {click_data.get('entity_type', 'N/A')}")
        if click_data['entity_type'] == 'npc':
            print(f"    NPC Name: {click_data.get('npc_name', 'N/A')}")
            print(f"    NPC ID: {click_data.get('npc_id', 'N/A')}")
            print(f"    NPC Index: {click_data.get('npc_index', 'N/A')}")
        elif click_data['entity_type'] == 'object':
            print(f"    Object Name: {click_data.get('object_name', 'N/A')}")
            print(f"    Object ID: {click_data.get('object_id', 'N/A')}")
            if 'object_tile' in click_data:
                tile = click_data['object_tile']
                print(f"    Object Tile: ({tile.get('x', 'N/A')}, {tile.get('y', 'N/A')}, plane: {tile.get('plane', 'N/A')})")
        elif click_data['entity_type'] == 'widget':
            if 'widget' in click_data:
                widget = click_data['widget']
                print(f"    Widget ID: {widget.get('id', 'N/A')}")
                print(f"    Widget Type: {widget.get('type', 'N/A')}")
                if 'text' in widget:
                    print(f"    Widget Text: {widget['text']}")
                if 'name' in widget:
                    print(f"    Widget Name: {widget['name']}")
                if 'bounds' in widget:
                    bounds = widget['bounds']
                    print(f"    Widget Bounds: x={bounds.get('x', 'N/A')}, y={bounds.get('y', 'N/A')}, width={bounds.get('width', 'N/A')}, height={bounds.get('height', 'N/A')}")
                if 'parent_id' in widget:
                    print(f"    Parent ID: {widget.get('parent_id', 'N/A')}")
                if 'child_index' in widget:
                    print(f"    Child Index: {widget.get('child_index', 'N/A')}")
                # NEW: Print child texts if present
                if 'child_texts' in widget:
                    child_texts = widget['child_texts']
                    if child_texts:
                        print("    Child Texts:")
                        for text in child_texts:
                            print(f"      - {text}")
    if click_data.get('type') == 'middle_mouse_press' and 'camera' in click_data:
        camera = click_data['camera']
        print(f"  Camera: pitch={camera.get('pitch', 'N/A')}, yaw={camera.get('yaw', 'N/A')}, zoom={camera.get('zoom', 'N/A')}")

    if 'widget_changes' in click_data:
        changes = click_data['widget_changes']
        if changes:
            # Separate text changes and sprite changes
            text_changes = []
            sprite_changes = []
            for change in changes:
                has_text = 'old_text' in change or 'new_text' in change
                has_sprite = 'old_sprite' in change or 'new_sprite' in change
                if has_text and not has_sprite:
                    text_changes.append(change)
                else:
                    sprite_changes.append(change)
            
            # Print text changes if enabled (all of them)
            if print_text and text_changes:
                print("  Text Widget Changes:")
                for change in text_changes:
                    print(f"    Type: {change.get('type', 'N/A')}, Widget ID: {change.get('widget_id', 'N/A')}, Path: {change.get('path', 'N/A')}")
                    if 'name' in change:
                        print(f"      Name: {change.get('name', 'N/A')}")
                    print(f"      Old Text: {change.get('old_text', 'N/A')}")
                    print(f"      New Text: {change.get('new_text', 'N/A')}")
            
            # Print sprite changes, limited by max_changes
            if sprite_changes:
                limited_sprite_changes = sprite_changes if max_changes is None else sprite_changes[:max_changes]
                if limited_sprite_changes:
                    print("  Sprite Widget Changes:")
                    for change in limited_sprite_changes:
                        print(f"    Type: {change.get('type', 'N/A')}, Widget ID: {change.get('widget_id', 'N/A')}, Path: {change.get('path', 'N/A')}")
                        if 'name' in change:
                            print(f"      Name: {change.get('name', 'N/A')}")
                        print(f"      Old Sprite: {change.get('old_sprite', 'N/A')}, New Sprite: {change.get('new_sprite', 'N/A')}")                        
                        if 'old_text' in change:
                            print(f"      Old Text: {change['old_text']}")
                        if 'new_text' in change:
                            print(f"      New Text: {change['new_text']}")

def clear_clicks() -> bool:
    """
    Clear all stored recent clicks on the server side.
    
    Returns:
        bool: True if cleared successfully, False otherwise.
    """
    params = {"function": "clear_clicks"}
    response = _default_client.send_request('click', params)
    if response and 'data' in response:
        data = response['data']
        if data.get("status") == "cleared":
            cleared = data.get("cleared_count", "unknown")
            print(f"Recent clicks cleared successfully ({cleared} removed).")
            return True
    print("Failed to clear clicks (no response or error).")
    return False


def get_last_click(print_text: bool = True, max_changes: Optional[int] = None) -> Optional[Dict[str, Any]]:
    """
    Retrieve the most recent click data from the ClickHandler and print it.

    Args:
        print_text (bool): Whether to print text-related widget changes (default: True).
        max_changes (Optional[int]): Maximum number of sprite-related widget changes to print (default: None, meaning all).

    Returns:
        Optional[Dict[str, Any]]: Last click data or None if request fails.
    """
    params = {"function": "last_click"}
    response = _default_client.send_request('click', params)
    if response and 'data' in response:
        click_data = response['data']
        if click_data:
            print("Last Click Data:")
            _print_click_data(click_data, print_text=print_text, max_changes=max_changes)
        else:
            print("No recent clicks available.")
        return click_data
    print("Failed to retrieve last click.")
    return None

def get_recent_clicks(limit: int = 5, print_text: bool = True, max_changes: Optional[int] = None) -> Optional[List[Dict[str, Any]]]:
    """
    Retrieve recent click data from the ClickHandler (up to the specified limit) and print them.

    Args:
        limit (int): Number of recent clicks to retrieve (default: 5, max: 10).
        print_text (bool): Whether to print text-related widget changes (default: True).
        max_changes (Optional[int]): Maximum number of sprite-related widget changes to print (default: None, meaning all).

    Returns:
        Optional[List[Dict[str, Any]]]: List of recent click data or None if request fails.
    """
    params = {"function": "recent_clicks", "limit": limit}
    response = _default_client.send_request('click', params)
    if response and 'data' in response:
        clicks = response['data']
        if clicks:
            print(f"\nRecent Clicks (last {len(clicks)}):")
            for i, click_data in enumerate(clicks, 1):
                print(f"\nClick #{i}:")
                _print_click_data(click_data, print_text=print_text, max_changes=max_changes)
        else:
            print("No recent clicks available.")
        return clicks
    print("Failed to retrieve recent clicks.")
    return None






def get_raw_recent_clicks(limit: int = 50) -> List[Dict[str, Any]]:
    """
    Fetch raw recent click data without any printing.
    """
    params = {"function": "recent_clicks", "limit": limit}
    response = _default_client.send_request('click', params)
    if response and 'data' in response:
        return response['data']
    return []


def get_minimap_click_functions(limit: int = 50):
    """
    Print clean, ready-to-copy click_minimap_tile() calls for recent minimap clicks.
    Newest click is always #1 (easiest to copy-paste).
    Only the function call is printed — no extra comments.
    """
    clicks = get_raw_recent_clicks(limit)
    minimap_clicks = [c for c in clicks if c.get('is_minimap_click')]
    
    print(f"\nMinimap click functions (last {len(minimap_clicks)}):")
    
    if not minimap_clicks:
        print("  No recent minimap clicks.")
        return
    
    # Server returns oldest → newest → reverse so newest is #1
    minimap_clicks = list(reversed(minimap_clicks))
    
    for i, click in enumerate(minimap_clicks, 1):
        tile = click.get('minimap_tile', {})
        if not tile or 'x' not in tile or 'y' not in tile:
            continue
        
        x = tile['x']
        y = tile['y']
        plane = tile.get('plane', 0)
        
        func_args = f"{x}, {y}"
        tile_str = f"({x}, {y})"
        if plane != 0:
            func_args += f", plane={plane}"
            tile_str = f"({x}, {y}, plane={plane})"
        
        func_call = f"click_minimap_tile({func_args}, rand_x=2, rand_y=2, target_zoom=2.0)"
        
        print(f"# {i}")
        print(f"if not {func_call}:")
        print(f"    print(\"Failed to click minimap tile {tile_str}\")")
        print("    exit()")
        print("else:")
        print("    wait_till_character_stopped_moving()")
        print()





def get_widget_click_functions(limit: int = 50):
    """
    Print clean, ready-to-copy click_widget() calls for recent widget clicks
    that resulted in a 'new' sprite on the *clicked widget itself*.
    This is perfect for capturing tab/button clicks (e.g. Equipment tab)
    where the button gets highlighted with a new sprite after being clicked.

    Newest qualifying click is always #1.
    """
    clicks = get_raw_recent_clicks(limit)
    
    items = []
    
    # Server returns oldest → newest → we reverse to process newest first
    for click in reversed(clicks):
        if click.get('entity_type') != 'widget':
            continue
        widget_data = click.get('widget', {})
        if 'id' not in widget_data:
            continue
        
        clicked_id = widget_data['id']
        new_sprite = None
        
        if 'widget_changes' in click:
            for change in click.get('widget_changes', []):
                if (change.get('type') == 'new' and
                    change.get('widget_id') == clicked_id and
                    'new_sprite' in change and
                    change['new_sprite'] != -1):
                    new_sprite = change['new_sprite']
                    # Take the first matching 'new' sprite (usually only one)
                    break
        
        if new_sprite is not None:
            items.append({
                'widget_id': clicked_id,
                'sprite_id': new_sprite,
                'tick': click.get('tick', 'N/A'),
                'option': click.get('option', '')
            })
    
    print(f"\nWidget click functions (new sprite on clicked widget, last {len(items)}):")
    
    if not items:
        print("  No recent widget clicks with a new sprite on the clicked widget.")
        return
    
    for i, item in enumerate(items, 1):
        widget_str = f"'{item['widget_id']}'"
        func_call = (
            f"click_widget({widget_str}, sprite_id={item['sprite_id']}, "
            f"hidden=False, right_click=False, action=None, "
            f"rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0))"
        )
        print(f"# {i}")
        print(f"if not {func_call}:")
        print(f"   exit(f'click widget {item['widget_id']} failed, exiting... time: {{time.strftime(\"%H:%M:%S\")}}')")
        

def get_recent_walk_clicks(limit: int = 10) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch recent clicks (up to the limit), filter for "Walk here" actions, and print them in a numbered format like:
    
    Recent Walk Clicks (last N):
      # 1: click_tile(x, y, plane=z, action="Walk here", tile_radius=2, right_click=False)
      # 2: ...
    
    Args:
        limit (int): Number of recent clicks to check (default: 5, max: 10).
    
    Returns:
        List of matching walk click data (raw) or None if request fails.
    """
    clicks = get_raw_recent_clicks(limit=limit)
    if not clicks:
        print("No recent clicks available.")
        return None
    
    walk_clicks = []
    for click_data in clicks:
        option = click_data.get('option', '')
        if option == 'Walk here' and click_data.get('type') == 'menu_option':
            # Get the tile: prefer 'clicked_tile' if present, else 'minimap_tile'
            tile = click_data.get('clicked_tile') or click_data.get('minimap_tile')
            if tile:
                walk_clicks.append((click_data, tile))
    
    if not walk_clicks:
        print("No 'Walk here' clicks in recent history.")
        return []
    
    # Reverse to make newest #1
    walk_clicks = list(reversed(walk_clicks))
    
    print(f"Recent Walk Clicks (last {len(walk_clicks)}):")
    raw_walks = []
    for i, (click_data, tile) in enumerate(walk_clicks, 1):
        x = tile.get('x', 'N/A')
        y = tile.get('y', 'N/A')
        plane = tile.get('plane', 0)
        
        # Hardcoded defaults as before
        action = "Walk here"
        tile_radius = 2
        right_click = False  # Adjust if needed for right-click detection
        
        func_call = f"click_tile({x}, {y}, plane={plane}, action=\"{action}\", tile_radius={tile_radius}, right_click={right_click})"
        tile_str = f"({x}, {y})" if plane == 0 else f"({x}, {y}, plane={plane})"
        
        print(f"# {i}")
        print("for i in range(3):")
        print(f"    if {func_call}:")
        print("       if wait_till_character_stopped_moving():")
        print("            break")
        print("    if i == 2:")
        print(f"        exit(\"Failed to walk to {tile_str}\")")
        print()
        
        raw_walks.append(click_data)
    
    return raw_walks


def get_recent_npc_clicks(limit: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch recent clicks (up to the limit), filter for NPC menu_option clicks, and print them in a numbered format like:
    
    Recent NPC Clicks (last N):
      # 1: click_closest_npc('npc name', option='option text', max_attempts=5)
      # 2: ...
    
    Names and options are converted to lowercase for consistency.
    
    Args:
        limit (int): Number of recent clicks to check (default: 5, max: 10).
    
    Returns:
        List of matching NPC click data (raw) or None if request fails.
    """
    clicks = get_raw_recent_clicks(limit=limit)
    if not clicks:
        print("No recent clicks available.")
        return None
    
    npc_clicks = []
    for click_data in clicks:
        if (click_data.get('entity_type') == 'npc' and
            click_data.get('type') == 'menu_option'):
            npc_name = click_data.get('npc_name')
            option = click_data.get('option')
            if npc_name and option:
                npc_clicks.append((click_data, npc_name.lower(), option.lower()))
    
    if not npc_clicks:
        print("No NPC menu_option clicks in recent history.")
        return []
    
    # Reverse to make newest #1
    npc_clicks = list(reversed(npc_clicks))
    
    print(f"Recent NPC Clicks (last {len(npc_clicks)}):")
    raw_npc_clicks = []
    for i, (click_data, npc_name, option) in enumerate(npc_clicks, 1):
        func_call = f"click_closest_npc('{npc_name}', option='{option}', max_attempts=5)"
        print(f"# {i}")
        print("for i in range(10):")
        print(f"    if not {func_call}:")
        print("        wait_for_next_tick()")
        print("    else:")
        print("        if wait_till_character_stopped_moving():")
        print("            break")
        print("    if i == 9:")
        print(f"        exit(\"Failed to click npc ({npc_name})\")")
        print()
        raw_npc_clicks.append(click_data)
    
    return raw_npc_clicks

def get_recent_object_clicks(limit: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch recent clicks (up to the limit), filter for object menu_option clicks, and print them in a numbered format like:
    
    Recent Object Clicks (last N):
      # 1: click_object("object_id", 'option text', tile=(x, y), radius=20)
      # 2: ...
    
    Options are converted to lowercase for consistency. Assumes plane=0 for the tile.
    
    Args:
        limit (int): Number of recent clicks to check (default: 5, max: 10).
    
    Returns:
        List of matching object click data (raw) or None if request fails.
    """
    clicks = get_raw_recent_clicks(limit=limit)
    if not clicks:
        print("No recent clicks available.")
        return None
    
    object_clicks = []
    for click_data in clicks:
        if (click_data.get('entity_type') == 'object' and
            click_data.get('type') == 'menu_option'):
            object_id = click_data.get('object_id')
            option = click_data.get('option')
            tile = click_data.get('object_tile')
            if object_id is not None and option and tile:
                object_clicks.append((click_data, str(object_id), option.lower(), tile))
    
    if not object_clicks:
        print("No object menu_option clicks in recent history.")
        return []
    
    # Reverse to make newest #1
    object_clicks = list(reversed(object_clicks))
    
    print(f"Recent Object Clicks (last {len(object_clicks)}):")
    raw_object_clicks = []
    for i, (click_data, object_id, option, tile) in enumerate(object_clicks, 1):
        x = tile.get('x', 'N/A')
        y = tile.get('y', 'N/A')
        # Assume plane=0, not including it in tile tuple
        func_call = f"click_gameobject(\"{object_id}\", '{option}', tile=({x}, {y}), radius=20)"
        object_name = click_data.get('object_name', '').lower()
        print(f"# {i}")
        print("for i in range(5):")
        print(f"    if {func_call}:")
        print("        break")
        print("    wait_for_next_tick()")
        print("    if i == 4:")
        print(f"        exit(\"Failed to click object ({object_name}, {option})\")")
        print()
        raw_object_clicks.append(click_data)
    
    return raw_object_clicks

def get_recent_inventory_clicks(limit: int = 5) -> Optional[List[Dict[str, Any]]]:
    """
    Fetch recent clicks (up to the limit), filter for inventory item menu_option clicks (widget with non-empty target),
    and print them in a numbered format like:
    
    Recent Inventory Clicks (last N):
      # 1: click_inventory('item name', action='option text', hover_only=False)
      # 2: ...
    
    Names and options are converted to lowercase for consistency.
    
    Args:
        limit (int): Number of recent clicks to check (default: 5, max: 10).
    
    Returns:
        List of matching inventory click data (raw) or None if request fails.
    """
    clicks = get_raw_recent_clicks(limit=limit)
    if not clicks:
        print("No recent clicks available.")
        return None
    
    inventory_clicks = []
    for click_data in clicks:
        if (click_data.get('entity_type') == 'widget' and
            click_data.get('type') == 'menu_option'):
            target = click_data.get('target', '').strip()
            option = click_data.get('option', '')
            if target and option:
                inventory_clicks.append((click_data, target.lower(), option.lower()))
    
    if not inventory_clicks:
        print("No inventory menu_option clicks (widget with target) in recent history.")
        return []
    
    # Reverse to make newest #1
    inventory_clicks = list(reversed(inventory_clicks))
    
    print(f"Recent Inventory Clicks (last {len(inventory_clicks)}):")
    raw_inventory_clicks = []
    for i, (click_data, name, action) in enumerate(inventory_clicks, 1):
        func_call = f"click_inventory('{name}', action='{action}', hover_only=False)"
        print(f"# {i}")
        print("for i in range(5):")
        print(f"    if {func_call}:")
        print("        break")
        print("    wait_for_next_tick()")
        print("    if i == 4:")
        print(f"        exit(\"Failed to click inventory ({name})\")")
        print()
        raw_inventory_clicks.append(click_data)
    
    return raw_inventory_clicks

previous_tick = None
previous_camera = None
was_changing = False
camera_print_count = 0   # <-- Add this global variable at the top with the other globals


def get_camera_changes(speed: int = 10):
    """
    Monitors camera yaw, pitch, and zoom changes between ticks.
    Delays printing until the camera stabilizes (a tick with no changes after changes occurred).
    Prints in a ready-to-copy retry block format.
    """
    global previous_tick, previous_camera, was_changing, camera_print_count

    # Fetch current game tick to initialize if needed
    current_tick = gametick().get('data', None)
    if current_tick is None:
        return

    # Initialize on first call (no print)
    if previous_tick is None or previous_camera is None:
        previous_tick = current_tick
        previous_camera = player().get('data', {}).get('camera', {})
        return

    # Wait for the next tick to check changes that occurred during the previous tick
    wait_for_next_tick()

    # Now fetch updated data after the tick
    current_tick = gametick().get('data', None)
    if current_tick is None or current_tick <= previous_tick:
        return  # No new tick, skip

    current_camera = player().get('data', {}).get('camera', {})
    if current_camera:
        # Check if values changed since last tick
        changed = (
            current_camera.get('pitch') != previous_camera.get('pitch') or
            current_camera.get('yaw') != previous_camera.get('yaw') or
            current_camera.get('zoom') != previous_camera.get('zoom')
        )
        
        if changed:
            # Camera is still changing
            was_changing = True
        else:
            # No change this tick; if it was changing before, print the stable values now
            if was_changing:
                pitch = current_camera.get('pitch', 'N/A')
                yaw = current_camera.get('yaw', 'N/A')
                zoom = current_camera.get('zoom', 'N/A')

                camera_print_count += 1

                print(f"# {camera_print_count}")
                print("for i in range(3):")
                print(f"    if camera(pitch={pitch}, yaw={yaw}, zoom={zoom}, speed={speed}):")
                print("        break")
                print("    if i == 2:")
                print('        exit("Failed to set camera")')
                print()

                was_changing = False
        
        # Always update previous for next comparison
        previous_camera = current_camera.copy()
    previous_tick = current_tick

import time

event_count = 0
last_clicks = []
seen_ticks = set()  # Track processed ticks to prevent duplicates

def monitor_actions(speed: int = 10):
    """
    Monitors all actions including camera changes and clicks, printing them in order with retry logic.
    Runs in a loop, checking per tick.
    """
    global previous_tick, previous_camera, was_changing, event_count, last_clicks

    while True:
        # Camera check logic
        current_tick = gametick().get('data', None)
        if current_tick is None:
            time.sleep(0.1)
            continue

        # Initialize if needed
        if previous_tick is None or previous_camera is None:
            previous_tick = current_tick
            previous_camera = player().get('data', {}).get('camera', {})
            continue

        # Wait for next tick
        wait_for_next_tick()

        # Fetch new tick
        current_tick = gametick().get('data', None)
        if current_tick is None or current_tick <= previous_tick:
            continue

        current_camera = player().get('data', {}).get('camera', {})
        if current_camera:
            changed = (
                current_camera.get('pitch') != previous_camera.get('pitch') or
                current_camera.get('yaw') != previous_camera.get('yaw') or
                current_camera.get('zoom') != previous_camera.get('zoom')
            )
            
            if changed:
                was_changing = True
            else:
                if was_changing:
                    pitch = current_camera.get('pitch', 'N/A')
                    yaw = current_camera.get('yaw', 'N/A')
                    zoom = current_camera.get('zoom', 'N/A')
                    event_count += 1
                    print(f"# {event_count}")
                    print("for i in range(3):")
                    print(f"    if camera(pitch={pitch}, yaw={yaw}, zoom={zoom}, speed={speed}):")
                    print("        break")
                    print("    if i == 2:")
                    print('        exit("Failed to set camera")')
                    print()
                    was_changing = False
            
            previous_camera = current_camera.copy()
        previous_tick = current_tick

        # Check for new clicks
        new_clicks = get_raw_recent_clicks(50)
        new_ones = [c for c in new_clicks if c.get('tick') not in seen_ticks]

        for click in new_ones:
            tick = click.get('tick')
            if tick in seen_ticks:
                continue
            seen_ticks.add(tick)

            event_count += 1
            print(f"# {event_count}")

            # Minimap click
            if click.get('is_minimap_click') and 'minimap_tile' in click:
                tile = click['minimap_tile']
                tx = tile.get('x')
                ty = tile.get('y')
                
                print("for i in range(10):")
                print(f"    if click_minimap_tile({tx}, {ty}, rand_x=2, rand_y=2, target_zoom=2.0):")
                print(f"        print(\"clicked minimap tile ({tx}, {ty})\")")
                print("       if wait_till_character_stopped_moving():")
                print("            break")
                print("    wait_for_next_tick()")
                print("    if i == 9:")
                print(f"        exit(\"Failed to click minimap tile ({tx}, {ty})\")")
                print()
                continue

            # Ground "Walk here" click
            elif click.get('option') == 'Walk here' and click.get('clicked_tile'):
                tile = click.get('clicked_tile')
                x = tile.get('x')
                y = tile.get('y')
                plane = tile.get('plane', 0)
                func_call = f"click_tile({x}, {y}, plane={plane}, action=\"Walk here\", tile_radius=2, right_click=False)"
                tile_str = f"({x}, {y})" if plane == 0 else f"({x}, {y}, plane={plane})"
                print("for i in range(3):")
                print(f"    if {func_call}:")
                print("       if wait_till_character_stopped_moving():")
                print("            break")
                print("    if i == 2:")
                print(f"        exit(\"Failed to walk to {tile_str}\")")
                print()
                continue

            # Sprite-changing widget (tabs/buttons) — includes "Worn Equipment" tab open
            elif (click.get('entity_type') == 'widget' and 
                  'widget_changes' in click and 
                  any(ch.get('type') == 'new' and 
                      ch.get('widget_id') == click['widget'].get('id') and 
                      ch.get('new_sprite') != -1 for ch in click['widget_changes'])):
                widget_id = click['widget']['id']
                new_sprite = next(ch['new_sprite'] for ch in click['widget_changes'] 
                                 if ch.get('type') == 'new' and 
                                    ch.get('widget_id') == widget_id and 
                                    ch.get('new_sprite') != -1)
                widget_str = f"'{widget_id}'"
                func_call = f"click_widget({widget_str}, sprite_id={new_sprite}, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0))"
                print(f"if not {func_call}:")
                print(f"   exit(f'click widget {widget_id} failed, exiting... time: {{time.strftime(\"%H:%M:%S\")}}')")
                print()
                continue

            # Prayer toggle
            elif (click.get('option', '').lower() in ['activate', 'deactivate'] and 
                  click.get('target', '').strip() and 
                  click.get('entity_type') == 'widget'):
                prayer_name = click.get('target', '').lower()
                option = click.get('option', '').lower()
                widget_id = click['widget'].get('id')
                widget_str = f"'{widget_id}'"
                func_call = f"click_widget({widget_str}, action='{option}', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0))"
                print("for i in range(5):")
                print(f"    if {func_call}:")
                print("        break")
                print("    wait_for_next_tick()")
                print("    if i == 4:")
                print(f"        exit(\"Failed to {option} prayer ({prayer_name})\")")
                print()
                continue

            # Equipment "Remove" action — handles jewelry + all other equipped items
            elif (click.get('entity_type') == 'widget' and
                  click.get('type') == 'menu_option' and
                  click.get('option', '').lower() == 'remove' and
                  click.get('target', '').strip()):
                raw_item_name = click.get('target', '').strip()
                
                jewelry_bases = [
                    'amulet of glory',
                    'ring of dueling',
                    'games necklace',
                    'combat bracelet',
                    'ring of wealth'
                ]
                
                lower_name = raw_item_name.lower()
                is_jewelry = any(base in lower_name for base in jewelry_bases)
                
                if is_jewelry:
                    import re
                    item_name = re.sub(r'\(\d+\)$', '', raw_item_name).strip()
                    exact_match = False
                else:
                    item_name = raw_item_name
                    exact_match = True
                
                print("for i in range(5):")
                print(f'    if click_widget_by_name("{item_name}", action="Remove", exact_match={exact_match}):')
                print("        break")
                print("    wait_for_next_tick()")
                print("    if i == 4:")
                print(f'        exit("Failed to remove equipment item: {raw_item_name}")')
                print()
                continue

            # Equipped jewelry action (teleport locations or Rub) — excludes Remove
            elif (click.get('entity_type') == 'widget' and
                  click.get('target', '').strip() and
                  click.get('option', '').lower() != 'remove'):
                raw_target = click.get('target', '').strip().lower()
                option = click.get('option')
                
                jewelry_map = {
                    'amulet of glory': 'click_equipped_glory',
                    'ring of dueling': 'click_equipped_ring_of_dueling',
                    'games necklace': 'click_equipped_games_necklace',
                    'combat bracelet': 'click_equipped_combat_bracelet',
                    'ring of wealth': 'click_equipped_ring_of_wealth'
                }
                
                matched_base = None
                for base in jewelry_map:
                    if base in raw_target:
                        matched_base = base
                        break
                
                if matched_base:
                    func_name = jewelry_map[matched_base]
                    print("for i in range(5):")
                    print(f"    if {func_name}(action='{option}'):") 
                    print("        wait_for_tile_change()")
                    print("        wait_for_next_tick()")
                    print("        break")
                    print("    wait_for_next_tick()")
                    print("    if i == 4:")
                    print(f'        exit("Failed to click equipped {matched_base} ({option})")')
                    print()
                    continue

            # Inventory jewelry action (lowest charge)
            elif (click.get('entity_type') == 'widget' and
                  click.get('target', '').strip() and
                  click.get('option')):
                raw_target = click.get('target', '').strip().lower()
                option = click.get('option')
                
                jewelry_map = {
                    'amulet of glory': 'click_lowest_glory',
                    'ring of dueling': 'click_lowest_ring_of_dueling',
                    'games necklace': 'click_lowest_games_necklace',
                    'combat bracelet': 'click_lowest_combat_bracelet',
                    'ring of wealth': 'click_lowest_ring_of_wealth'
                }
                
                matched_base = None
                for base in jewelry_map:
                    if base in raw_target:
                        matched_base = base
                        break
                
                if matched_base:
                    func_name = jewelry_map[matched_base]
                    print("for i in range(5):")
                    print(f"    if {func_name}(action='{option}'):") 
                    print("        break")
                    print("    wait_for_next_tick()")
                    print("    if i == 4:")
                    print(f'        exit("Failed to click lowest {matched_base} ({option})")')
                    print()
                    continue

            # Object click
            elif click.get('entity_type') == 'object':
                object_id = click.get('object_id')
                option = click.get('option', '').lower()
                tile = click.get('object_tile')
                if tile:
                    x = tile.get('x')
                    y = tile.get('y')
                    object_name = click.get('object_name', '').lower() or 'unknown'
                    func_call = f"click_gameobject(\"{object_id}\", '{option}', tile=({x}, {y}), radius=20)"
                    print("for i in range(5):")
                    print(f"    if {func_call}:")
                    print("        break")
                    print("    wait_for_next_tick()")
                    print("    if i == 4:")
                    print(f"        exit(\"Failed to click object ({object_name}, {option})\")")
                    print()
                continue

            # Generic inventory item action
            elif (click.get('entity_type') == 'widget' and
                  click.get('target', '').strip() and
                  click.get('option')):
                name = click.get('target', '').lower()
                action = click.get('option', '').lower()
                func_call = f"click_inventory('{name}', action='{action}', hover_only=False)"
                print("for i in range(5):")
                print(f"    if {func_call}:")
                print("        break")
                print("    wait_for_next_tick()")
                print("    if i == 4:")
                print(f"        exit(\"Failed to click inventory ({name})\")")
                print()
                continue

            # Dialogue / menu option on widget (no target)
            elif (click.get('entity_type') == 'widget' and 
                  click.get('type') == 'menu_option' and 
                  click.get('option') and 
                  not click.get('target', '').strip()):
                option = click.get('option', '').lower()
                widget_data = click.get('widget', {})
                widget_id = widget_data.get('id')
                
                if 'parent_id' in widget_data and 'child_index' in widget_data:
                    parent_id = widget_data['parent_id']
                    child_index = widget_data['child_index']
                    func_call = f"click_widget_child('{parent_id}', sprite_id=None, hidden=False, child_index={child_index}, right_click=False, action=None)"
                    fail_msg = f"Failed to click dialogue option ({option}) via child"
                else:
                    widget_str = f"'{widget_id}'"
                    func_call = f"click_widget({widget_str}, action='{option}', hidden=False, right_click=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0))"
                    fail_msg = f"Failed to click widget option ({option})"
                
                print("for i in range(5):")
                print(f"    if {func_call}:")
                print("        break")
                print("    wait_for_next_tick()")
                print("    if i == 4:")
                print(f"        exit(\"{fail_msg}\")")
                print()
                continue

            # NPC click
            elif click.get('entity_type') == 'npc':
                npc_name = click.get('npc_name', '').lower()
                option = click.get('option', '').lower()
                func_call = f"click_closest_npc('{npc_name}', option='{option}', max_attempts=5)"
                print("for i in range(10):")
                print(f"    if not {func_call}:")
                print("        wait_for_next_tick()")
                print("    else:")
                print("        if wait_till_character_stopped_moving():")
                print("            break")
                print("    if i == 9:")
                print(f"        exit(\"Failed to click npc ({npc_name})\")")
                print()
                continue

            # Unknown click
            else:
                print("# Unknown click type - skipping")
                print(click)
                print()

        # Update last_clicks
        last_clicks = new_clicks[-100:]

clear_clicks()
monitor_actions()


get_recent_clicks(limit=55, max_changes=55)





# get_minimap_click_functions()
# get_widget_click_functions()
# get_recent_walk_clicks()
# get_recent_npc_clicks()
# get_recent_object_clicks()
# get_recent_inventory_clicks()
# get_camera_changes()

