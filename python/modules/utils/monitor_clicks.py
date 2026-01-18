# monitor_clicks.py
# This file provides standalone functions to interact with the ClickHandler via the plugin server.
# It uses the _default_client from plugin_client.py to send requests and print click data.

from typing import Optional, Dict, List, Any

from modules.core.plugin_client import _default_client  # Adjusted import path based on your setup

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
                    print(f"      Old Text: {change.get('old_text', 'N/A')}")
                    print(f"      New Text: {change.get('new_text', 'N/A')}")
            
            # Print sprite changes, limited by max_changes
            if sprite_changes:
                limited_sprite_changes = sprite_changes if max_changes is None else sprite_changes[:max_changes]
                if limited_sprite_changes:
                    print("  Sprite Widget Changes:")
                    for change in limited_sprite_changes:
                        print(f"    Type: {change.get('type', 'N/A')}, Widget ID: {change.get('widget_id', 'N/A')}, Path: {change.get('path', 'N/A')}")
                        print(f"      Old Sprite: {change.get('old_sprite', 'N/A')}, New Sprite: {change.get('new_sprite', 'N/A')}")
                        if 'old_text' in change:
                            print(f"      Old Text: {change['old_text']}")
                        if 'new_text' in change:
                            print(f"      New Text: {change['new_text']}")

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
        
        if plane == 0:
            func_call = f"click_minimap_tile({x}, {y}, rand_x=2, rand_y=2, target_zoom=2.0)"
        else:
            func_call = f"click_minimap_tile({x}, {y}, plane={plane}, rand_x=2, rand_y=2, target_zoom=2.0)"
        
        print(f"  #{i:2d}: {func_call}")





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
        
        print(f"  #{i:2d}: {func_call}")

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
        print(f"  #{i:2d}: {func_call}")
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
    
    print(f"Recent NPC Clicks (last {len(npc_clicks)}):")
    raw_npc_clicks = []
    for i, (click_data, npc_name, option) in enumerate(npc_clicks, 1):
        func_call = f"click_closest_npc('{npc_name}', option='{option}', max_attempts=5)"
        print(f"  #{i:2d}: {func_call}")
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
    
    print(f"Recent Object Clicks (last {len(object_clicks)}):")
    raw_object_clicks = []
    for i, (click_data, object_id, option, tile) in enumerate(object_clicks, 1):
        x = tile.get('x', 'N/A')
        y = tile.get('y', 'N/A')
        # Assume plane=0, not including it in tile tuple
        func_call = f"click_object(\"{object_id}\", '{option}', tile=({x}, {y}), radius=20)"
        print(f"  #{i:2d}: {func_call}")
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
    
    print(f"Recent Inventory Clicks (last {len(inventory_clicks)}):")
    raw_inventory_clicks = []
    for i, (click_data, name, action) in enumerate(inventory_clicks, 1):
        func_call = f"click_inventory('{name}', action='{action}', hover_only=False)"
        print(f"  #{i:2d}: {func_call}")
        raw_inventory_clicks.append(click_data)
    
    return raw_inventory_clicks

# while True:
# clear_clicks()
import time
# time.sleep(0.6)
# get_recent_clicks(limit=55, max_changes=55)
# get_minimap_click_functions()
# get_widget_click_functions()
# get_recent_walk_clicks(limit=10)
# get_recent_npc_clicks(limit=10)
# get_recent_object_clicks(limit=10)
# get_recent_inventory_clicks(limit=10)