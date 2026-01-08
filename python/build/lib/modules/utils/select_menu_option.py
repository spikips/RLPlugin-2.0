import random
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.core.plugin_client import interact_options
import time
import re


def select_menu_option(canvas_x: int, canvas_y: int, action: str, hover_only: bool = False) -> bool:
    """
    Right-click at canvas coordinates, open the menu, and select (or hover) the specified action.
    Returns True if the action was found and handled, False otherwise.
    """
    rl_x, rl_y = runelite_window(0, 0)
    screen_x = canvas_x + rl_x
    screen_y = canvas_y + rl_y

    # Right-click to open menu
    move(screen_x, screen_y, fast=True, sleep=True, button='right')
    time.sleep(random.uniform(0.05, 0.1))

    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available")
        return False

    action_normalized = ' '.join(action.lower().split())
    for option in options:
        option_target_clean = re.sub(r'<[^>]+>', '', option['target']).lower()
        option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
        if option['option'].lower() == action_normalized or option_combined == action_normalized:
            action_x = option['middle_point']['x'] + rl_x
            action_y = option['middle_point']['y'] + rl_y
            if hover_only:
                move(action_x, action_y, fast=True, sleep=False)  # Hover without click
            else:
                move(action_x, action_y, fast=True, sleep=True, button='left')
            return True

    print(f"No '{action}' option found in menu")
    return False

def check_widget(id_str, sprite_id=None, hidden=None, child_index=None):
    try:
        widget_id = int(id_str)
    except ValueError:
        print(f"Invalid widget ID: {id_str}")
        return False

    widgets = get_all_widget_data()

    if not widgets:
        print("No widget data available")
        return False

    def matches(widget):
        if widget.get("id") != widget_id:
            return False
        if sprite_id is not None and widget.get("spriteId") != sprite_id:
            return False
        if hidden is not None and widget.get("hidden") != hidden:
            return False
        return True

    # Check both top-level widgets and their children
    for widget in widgets:
        if matches(widget):
            return True
        if 'children' in widget and child_index is not None:
            children = widget.get('children', [])
            if child_index < len(children) and matches(children[child_index]):
                return True
        elif 'children' in widget:
            for child in widget.get('children', []):
                if matches(child):
                    return True

    return False

def click_widget(id_str, sprite_id=None, hidden=False, button='left', action=None):
    """
    Clicks a widget with the specified ID, optionally matching sprite_id and hidden status.
    Supports left or right click, and optionally selects an action from the context menu after right-clicking.
    
    Args:
        id_str (str): Widget ID as a string
        sprite_id (int, optional): Sprite ID to match
        hidden (bool, optional): Hidden status to match (default: False)
        button (str): Mouse button to use ('left' or 'right')
        action (str, optional): Context menu action to select after right-click (e.g., 'Use', 'Examine')
    
    Returns:
        bool: True if the widget was clicked or action selected, False otherwise
    """
    rl_x, rl_y = runelite_window(0, 0)
    try:
        widget_id = int(id_str)
    except ValueError:
        return False

    widgets = get_all_widget_data()
    if not widgets:
        return False

    for widget in widgets:
        if widget.get("id") != widget_id:
            continue
        if sprite_id is not None and widget.get("spriteId") != sprite_id:
            continue
        if hidden is not None and widget.get("hidden", False) != hidden:
            continue
        if 'bounds' in widget:
            bounds = widget['bounds']
            canvas_x = bounds['x'] + 1
            canvas_y = bounds['y'] + 1
            width = bounds['width']
            height = bounds['height']
            
            # Generate random coordinates within the widget bounds, avoiding edges
            random_x = canvas_x + random.randint(1, width - 2) + rl_x
            random_y = canvas_y + random.randint(1, height - 2) + rl_y
            # print(f'Widget clicking at: {random_x}, {random_y}, canvas: {canvas_x}, {canvas_y}, width: {width}, height: {height}')
            
            if button == 'right' and action:
                # Right-click and select action from context menu
                move(random_x, random_y, fast=True, sleep=True, button='right')
                time.sleep(random.uniform(0.05, 0.1))
                options = interact_options().get('data', [])
                if not options:
                    print("No interaction options available after right-click")
                    return False
                
                action_normalized = ' '.join(action.lower().split())
                for option in options:
                    option_target_clean = re.sub(r'<[^>]+>', '', option['target']).lower()
                    option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
                    if option['option'].lower() == action_normalized or option_combined == action_normalized:
                        action_x = option['middle_point']['x'] + rl_x
                        action_y = option['middle_point']['y'] + rl_y
                        print(f"Selecting context menu action: {option['option']} {option['target']}")
                        move(action_x, action_y, fast=True, sleep=True, button='left')
                        return True
                print(f"No '{action}' option found in context menu")
                return False
            else:
                # Perform the specified click (left or right)
                move(random_x, random_y, fast=True, sleep=True, button=button)
                return True

    return False

def click_widget_child(id_str, sprite_id=None, hidden=None, child_index=None, button='left', action=None):
    """
    Clicks a child widget with the specified ID, optionally matching sprite_id, hidden status, and child index.
    Supports left or right click, and optionally selects an action from the context menu after right-clicking.
    
    Args:
        id_str (str): Widget ID as a string
        sprite_id (int, optional): Sprite ID to match
        hidden (bool, optional): Hidden status to match
        child_index (int, optional): Index of the child widget to click
        button (str): Mouse button to use ('left' or 'right')
        action (str, optional): Context menu action to select after right-click (e.g., 'Use', 'Examine')
    
    Returns:
        bool: True if the widget was clicked or action selected, False otherwise
    """
    rl_x, rl_y = runelite_window(0, 0)
    try:
        widget_id = int(id_str)
    except ValueError:
        print(f"Invalid widget ID: {id_str}")
        return False

    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data available")
        return False

    # Find all widgets with the matching ID, including children
    matching_widgets = []
    for widget in widgets:
        if widget.get("id") == widget_id and 'bounds' in widget:
            matching_widgets.append(widget)
        if 'children' in widget:
            for child in widget.get('children', []):
                if child.get("id") == widget_id and 'bounds' in child:
                    matching_widgets.append(child)

    if not matching_widgets:
        print(f"No widgets found with ID {widget_id}")
        return False

    # Filter by hidden if specified
    if hidden is not None:
        matching_widgets = [w for w in matching_widgets if w.get("hidden") == hidden]

    # Prioritize the specified child_index if provided
    target_widget = None
    if child_index is not None:
        for widget in widgets:
            if 'children' in widget and widget.get("id") == widget_id:
                children = widget.get('children', [])
                if child_index < len(children):
                    candidate = children[child_index]
                    if candidate.get("id") == widget_id and 'bounds' in candidate and candidate['bounds'].get('width', 0) > 0 and candidate['bounds'].get('height', 0) > 0:
                        # If sprite_id is specified, check if it matches (already selected)
                        if sprite_id is not None and candidate.get("spriteId") == sprite_id:
                            print(f"Child {child_index} widget with ID {widget_id}, spriteId {sprite_id} is already in desired state")
                            return True
                        target_widget = candidate
                        print(f"Selected child {child_index} widget with ID {widget_id}, spriteId {candidate.get('spriteId')}, bounds {candidate['bounds']}")
                        break

    # Fallback: If no child_index specified or invalid, pick widget with largest bounds
    if not target_widget:
        matching_widgets = [
            w for w in matching_widgets if 'bounds' in w and w['bounds'].get('width', 0) > 0 and w['bounds'].get('height', 0) > 0
        ]
        if not matching_widgets:
            print(f"No clickable widgets found with ID {widget_id}")
            return False
        # Pick the widget with the largest area
        target_widget = max(matching_widgets, key=lambda w: w['bounds']['width'] * w['bounds']['height'])
        print(f"No child widget at index {child_index} or invalid, using widget with ID {widget_id}, spriteId {target_widget.get('spriteId')}, bounds {target_widget['bounds']}")

    # Perform the click
    bounds = target_widget['bounds']
    canvas_x = bounds['x'] + 1
    canvas_y = bounds['y'] + 1
    width = bounds['width']
    height = bounds['height']

    # Generate random coordinates within the widget bounds, avoiding edges
    random_x = canvas_x + random.randint(1, width - 2) + rl_x
    random_y = canvas_y + random.randint(1, height - 2) + rl_y

    if button == 'right' and action:
        # Right-click and select action from context menu
        print(f"Right-clicking widget at coordinates: ({random_x}, {random_y})")
        move(random_x, random_y, fast=True, sleep=True, button='right')
        time.sleep(random.uniform(0.05, 0.1))
        options = interact_options().get('data', [])
        if not options:
            print("No interaction options available after right-click")
            return False
        
        action_normalized = ' '.join(action.lower().split())
        for option in options:
            option_target_clean = re.sub(r'<[^>]+>', '', option['target']).lower()
            option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
            if option['option'].lower() == action_normalized or option_combined == action_normalized:
                action_x = option['middle_point']['x'] + rl_x
                action_y = option['middle_point']['y'] + rl_y
                print(f"Selecting context menu action: {option['option']} {option['target']}")
                move(action_x, action_y, fast=True, sleep=True, button='left')
                return True
        print(f"No '{action}' option found in context menu")
        return False
    else:
        # Perform the specified click (left or right)
        print(f"Clicking widget at coordinates: ({random_x}, {random_y}) with {button} button")
        move(random_x, random_y, fast=True, sleep=True, button=button)
        return True

def check_widget_text(id_str, child_index=None):
    """Retrieve the text from a widget or its child by ID and optional child index."""
    try:
        widget_id = int(id_str)
    except ValueError:
        print(f"Invalid widget ID: {id_str}")
        return None

    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data available")
        return None

    for widget in widgets:
        if widget.get("id") == widget_id:
            if child_index is None:
                return widget.get('text', '')
            else:
                children = widget.get('children', [])
                if 0 <= child_index < len(children):
                    return children[child_index].get('text', '')
                else:
                    print(f"Child index {child_index} out of range for widget {widget_id}")
                    return None

    # If not found in top-level, search in children recursively
    for widget in widgets:
        children = widget.get('children', [])
        for child in children:
            if child.get("id") == widget_id:
                return child.get('text', '')

    print(f"Widget with ID {widget_id} not found")
    return None