# monitor_clicks.py
# This file provides standalone functions to interact with the ClickHandler via the plugin server.
# It uses the _default_client from plugin_client.py to send requests and print click data.

from typing import Optional, Dict, List, Any

from modules.core.plugin_client import _default_client  # Adjusted import path based on your setup

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
            print(f"Recent Clicks (last {len(clicks)}):")
            for i, click_data in enumerate(clicks, 1):
                print(f"\nClick #{i}:")
                _print_click_data(click_data, print_text=print_text, max_changes=max_changes)
        else:
            print("No recent clicks available.")
        return clicks
    print("Failed to retrieve recent clicks.")
    return None

while True:
    import time
    time.sleep(0.6)
    get_recent_clicks(limit=50, max_changes=55)