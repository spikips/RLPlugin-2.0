import random
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.core.plugin_client import interact_options
import time
import re

def get_widget(id_str, sprite_id=None, child_index=None):
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
            return None
        if sprite_id is not None and widget.get("spriteId") != sprite_id:
            return None
        return widget
    
    def recursive_search(widget_list):
        for widget in widget_list:
            match = matches(widget)
            if match is not None:
                return match
            if 'children' in widget:
                child_result = recursive_search(widget.get('children', []))
                if child_result is not None:
                    return child_result
        return None

    found_widget = recursive_search(widgets)
    if found_widget is None:
        print(f"Widget with ID {widget_id} not found")
        return False

    if child_index is not None:
        if 'children' not in found_widget or not isinstance(found_widget['children'], list) or child_index >= len(found_widget['children']):
            print(f"Widget has no children or child_index {child_index} is out of range")
            return False
        return found_widget['children'][child_index]
    else:
        return found_widget

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

    def recursive_search(widget_list):
        for widget in widget_list:
            if matches(widget):
                return True
            if 'children' in widget:
                if recursive_search(widget.get('children', [])):
                    return True
        return False

    # If child_index specified, target that specific path (non-recursive for precision)
    if child_index is not None:
        for widget in widgets:
            if 'children' in widget:
                children = widget.get('children', [])
                if child_index < len(children) and matches(children[child_index]):
                    return True
        return False

    # Otherwise, full recursive search
    return recursive_search(widgets)

def click_widget(id_str, sprite_id=None, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
    """
    Modified to support right-click and action selection.
    - If right_click=False and action=None: Left-clicks the widget.
    - If right_click=True and action=None: Right-clicks the widget.
    - If action is provided: Right-clicks and selects the specified action using select_menu_option logic.
    - If middle_point=True: Clicks the middle of the widget, optionally randomized by rand_x and rand_y.
    - If middle_point=False: Clicks a random point within the widget (original behavior).
    - clicks: Number of times to click (default: 1).
    - sleep_interval: Tuple (min, max) for random sleep between clicks in seconds (default: (0, 0) for no sleep).
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
        if sprite_id is not None and widget.get("spriteId") == sprite_id:
            return True  # Already in desired state
        if hidden is not None and widget.get("hidden", False) != hidden:
            continue
        if 'bounds' in widget:
            bounds = widget['bounds']
            canvas_x = bounds['x'] + 1
            canvas_y = bounds['y'] + 1
            width = bounds['width']
            height = bounds['height']
            
            if rand_x > 0 or rand_y > 0:
                # Start at middle
                rel_x = width // 2
                rel_y = height // 2
                # Apply randomization if specified
                if rand_x > 0:
                    rel_x += random.randint(-rand_x, rand_x)
                if rand_y > 0:
                    rel_y += random.randint(-rand_y, rand_y)
                # Clamp to avoid edges
                # rel_x = max(1, min(rel_x, width - 2))
                # rel_y = max(1, min(rel_y, height - 2))
            else:
                # Original random behavior, avoiding edges
                rel_x = random.randint(1, width - 2)
                rel_y = random.randint(1, height - 2)
            
            abs_x = canvas_x + rel_x + rl_x
            abs_y = canvas_y + rel_y + rl_y
            # print(f'widget clicking at: {abs_x}, {abs_y}, canvas: {canvas_x}, {canvas_y}, width: {width}, height: {height}')
            
            for i in range(clicks):
                if i > 0 and sleep_interval != (0, 0):
                    time.sleep(random.uniform(sleep_interval[0], sleep_interval[1]))
                
                if action:
                    # Use select_menu_option logic for right-click + action
                    select_menu_option_logic(canvas_x + rel_x, canvas_y + rel_y, action)
                elif right_click:
                    # Right-click only
                    move(abs_x, abs_y, fast=True, sleep=True, button='right')
                else:
                    # Left-click (original behavior)
                    move(abs_x, abs_y, fast=True, sleep=True, button='left')
            return True

    return False

def click_widget_child(id_str, sprite_id=None, hidden=None, child_index=None, right_click=False, action=None):
    """
    Modified to support right-click and action selection.
    - If right_click=False and action=None: Left-clicks the widget/child.
    - If right_click=True and action=None: Right-clicks the widget/child.
    - If action is provided: Right-clicks and selects the specified action using select_menu_option logic.
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
        target_widget = max(matching_widgets, key=lambda w: w['bounds']['width'] * w['bounds']['height'])
        print(f"No child widget at index {child_index} or invalid, using widget with ID {widget_id}, spriteId {target_widget.get('spriteId')}, bounds {target_widget['bounds']}")

    # Perform the action
    bounds = target_widget['bounds']
    canvas_x = bounds['x'] + 1
    canvas_y = bounds['y'] + 1
    width = bounds['width']
    height = bounds['height']

    # Generate random relative coordinates
    rel_random_x = random.randint(1, width - 2)
    rel_random_y = random.randint(1, height - 2)
    abs_random_x = canvas_x + rel_random_x + rl_x
    abs_random_y = canvas_y + rel_random_y + rl_y

    print(f"Clicking at coordinates: ({abs_random_x}, {abs_random_y})")

    if action:
        # Use select_menu_option logic for right-click + action
        return select_menu_option_logic(rel_random_x + canvas_x, rel_random_y + canvas_y, action)
    elif right_click:
        # Right-click only
        move(abs_random_x, abs_random_y, fast=True, sleep=True, button='right')
    else:
        # Left-click (original)
        move(abs_random_x, abs_random_y, fast=True, sleep=True, button='left')
    return True

def select_menu_option_logic(rel_x: int, rel_y: int, action: str) -> bool:
    """
    Internal logic adapted from select_menu_option.py.
    Hovers over relative coords, right-clicks if needed, and selects the action.
    Returns True if successful.
    """
    rl_x, rl_y = runelite_window(0, 0)
    screen_x = rl_x + rel_x
    screen_y = rl_y + rel_y
    
    # Hover to load interaction options
    move(screen_x, screen_y, fast=True, sleep=True)
    time.sleep(random.uniform(0.05, 0.1))
    
    # Get available interaction options
    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available.")
        return False
    
    # Normalize action for comparison
    action_normalized = ' '.join(action.lower().split())
    
    # Check if the first option matches the desired action
    first_option = options[0]
    first_option_target_clean = re.sub(r'<[^>]+>', '', first_option['target']).lower()
    first_option_combined = f"{first_option['option'].lower()} {first_option_target_clean}".strip()
    
    if first_option['option'].lower() == action_normalized or first_option_combined == action_normalized:
        print(f"Matched first option: {first_option}")
        move(screen_x, screen_y, fast=True, sleep=True, button='left')
        return True
    
    # Look for the action in the context menu
    found_action = False
    action_x, action_y = 0, 0
    for option in options:
        option_target_clean = re.sub(r'<[^>]+>', '', option['target']).lower()
        option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
        
        if option['option'].lower() == action_normalized or option_combined == action_normalized:
            action_x = option['middle_point']['x'] + rl_x
            action_y = option['middle_point']['y'] + rl_y
            found_action = True
            break
    
    if found_action:
        # Right-click to open context menu
        move(screen_x, screen_y, fast=True, sleep=True, button='right')
        time.sleep(random.uniform(0.05, 0.1))
        # Move to the action and click
        move(action_x, action_y, fast=True, sleep=True, button='left')
        return True
    
    print(f"No '{action}' option found. Available options: {[f'{opt['option']} {re.sub(r'<[^>]+>', '', opt['target'])}' for opt in options]}")
    return False

def check_widget_text(id_str, child_index=None):
    """Retrieve the text from a widget or its child by ID and optional child index."""
    try:
        widget_id = int(id_str)
    except ValueError:
        print(f"Invalid widget ID: {id_str}")
        return None

    widgets = get_all_widget_data()
    # print(widgets)

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

def check_widget_name(id_str, child_index=None):
    """
    Retrieve the name from a widget or its child by ID and optional child index.
    Similar to check_widget_text, but returns the name instead of text.
    Automatically strips color tags like <col=ff9040>text</col>.
    
    Args:
        id_str (str): Widget ID to search for.
        child_index (int, optional): Specific child index if targeting a parent widget.
    
    Returns:
        str or None: The cleaned full name if found, None otherwise.
    """
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
                name = widget.get('name', '')
            else:
                children = widget.get('children', [])
                if 0 <= child_index < len(children):
                    name = children[child_index].get('name', '')
                else:
                    print(f"Child index {child_index} out of range for widget {widget_id}")
                    return None
            # Strip color tags
            cleaned_name = re.sub(r'<col=[^>]+>(.*?)</col>', r'\1', name)
            return cleaned_name.strip() if cleaned_name else ''

    # If not found in top-level, search in children recursively
    for widget in widgets:
        children = widget.get('children', [])
        for child in children:
            if child.get("id") == widget_id:
                name = child.get('name', '')
                # Strip color tags
                cleaned_name = re.sub(r'<col=[^>]+>(.*?)</col>', r'\1', name)
                return cleaned_name.strip() if cleaned_name else ''

    print(f"Widget with ID {widget_id} not found")
    return None

def click_widget_by_name(name_str, sprite_id=None, hidden=None, exact_match=False, child_index=None, right_click=False, action=None, middle_point=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
    """
    Clicks a widget or child by name (case-insensitive partial or exact match), similar to click_widget.
    First finds the widget using check_widget_name logic, then clicks it.
    
    Args:
        name_str (str): Name to search for.
        sprite_id (int, optional): Filter by sprite ID.
        hidden (bool, optional): Filter by hidden status.
        exact_match (bool, optional): If True, require exact name match (case-insensitive) on the plain text (color/img tags stripped).
                                     If False (default), use partial substring match on the plain text.
        child_index (int, optional): Specific child index if targeting a parent widget.
        right_click (bool): Right-click instead of left-click (default: False).
        action (str): If provided, right-click and select the action (default: None).
        middle_point (bool): Click middle (default: False, random point).
        rand_x, rand_y (int): Random offset from middle (default: 0).
        clicks (int): Number of clicks (default: 1).
        sleep_interval (tuple): (min, max) sleep between clicks (default: (0, 0)).
    
    Returns:
        bool: True if clicked successfully, False otherwise.
    """
    # First, find the target widget using recursive search (similar to check_widget_name)
    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data available")
        return False

    # Normalize target name (strip whitespace and lowercase)
    name_normalized = name_str.strip().lower()

    def strip_tags(text):
        """Remove all RuneScape-style tags like <col=ff9040>, </col>, <img=5>, etc."""
        if not text:
            return ""
        return re.sub(r'<[^>]*>', '', text).strip()

    def matches(widget):
        widget_name_raw = widget.get("name", "")
        widget_name_plain = strip_tags(widget_name_raw).lower()
        
        if exact_match:
            if widget_name_plain != name_normalized:
                return False
        else:
            if name_normalized not in widget_name_plain:
                return False
                
        if sprite_id is not None and widget.get("spriteId") != sprite_id:
            return False
        if hidden is not None and widget.get("hidden") != hidden:
            return False
        return True

    def recursive_find(widget_list):
        for widget in widget_list:
            if matches(widget):
                return widget
            if 'children' in widget:
                result = recursive_find(widget.get('children', []))
                if result is not None:
                    return result
        return None

    # If child_index specified, target that specific path
    if child_index is not None:
        target_widget = None
        for widget in widgets:
            if 'children' in widget:
                children = widget.get('children', [])
                if child_index < len(children) and matches(children[child_index]):
                    target_widget = children[child_index]
                    break
    else:
        target_widget = recursive_find(widgets)

    if target_widget is None:
        match_type = "exactly matching" if exact_match else "containing"
        print(f"No widget found with plain name {match_type} '{name_str}' (tags stripped for comparison)")
        return False

    # Now click it (reuse logic from click_widget)
    rl_x, rl_y = runelite_window(0, 0)
    if 'bounds' not in target_widget:
        print("Target widget has no bounds")
        return False

    bounds = target_widget['bounds']
    canvas_x = bounds['x'] + 1
    canvas_y = bounds['y'] + 1
    width = bounds['width']
    height = bounds['height']
    
    if middle_point:
        # Start at middle
        rel_x = width // 2
        rel_y = height // 2
        # Apply randomization if specified
        if rand_x > 0:
            rel_x += random.randint(-rand_x, rand_x)
        if rand_y > 0:
            rel_y += random.randint(-rand_y, rand_y)
        # Clamp to avoid edges
        rel_x = max(1, min(rel_x, width - 2))
        rel_y = max(1, min(rel_y, height - 2))
    else:
        # Random behavior, avoiding edges
        rel_x = random.randint(1, width - 2)
        rel_y = random.randint(1, height - 2)
    
    abs_x = canvas_x + rel_x + rl_x
    abs_y = canvas_y + rel_y + rl_y
    raw_name = target_widget.get("name", "")
    plain_name = strip_tags(raw_name)
    # Changed fancy arrow → to ASCII -> to avoid UnicodeEncodeError on Windows consoles
    print(f'clicking widget by name at: {abs_x}, {abs_y}, canvas: {canvas_x}, {canvas_y}, width: {width}, height: {height} | raw: "{raw_name}" -> plain: "{plain_name}"')
    
    for i in range(clicks):
        if i > 0 and sleep_interval != (0, 0):
            time.sleep(random.uniform(sleep_interval[0], sleep_interval[1]))
        
        if action:
            # Use select_menu_option logic for right-click + action
            if select_menu_option_logic(canvas_x + rel_x, canvas_y + rel_y, action):
                return True
            return False
        elif right_click:
            # Right-click only
            move(abs_x, abs_y, fast=True, sleep=True, button='right')
        else:
            # Left-click
            move(abs_x, abs_y, fast=True, sleep=True, button='left')
    return True

# Example usage for debugging
# while True:
# click_widget(35913778)
# click_widget('10485782')  # Slightly reduced sleep for tighter timing


# print(click_widget_child('8454157', child_index=1))
# print(click_widget('8454157', sprite_id=699))
# click_widget('8454150')
# print(check_widget('8454157', sprite_id=699, child_index=100))
# print(check_widget_text('8454157', child_index=1))
# print(check_widget('8454157', child_index=4, sprite_id=699))
print(check_widget('35913796', sprite_id=1030))
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')
# click_widget_by_name("Monk's robe top", action="remove", exact_match=True)