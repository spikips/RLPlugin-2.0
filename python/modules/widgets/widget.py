import random
from modules.utils.select_menu_option import select_menu_option
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import get_runelite_window_coords, runelite_window
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

def click_widget(id_str, sprite_id=None, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0), fast=False):
    """
    Modified to support right-click and action selection.
    - If right_click=False and action=None: Left-clicks the widget.
    - If right_click=True and action=None: Right-clicks the widget.
    - If action is provided: Right-clicks and selects the specified action using select_menu_option
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
            # Use the same safe-canvas logic as click_widget_child: no +1 offset
            canvas_x = bounds['x']
            canvas_y = bounds['y']
            width = bounds['width']
            height = bounds['height']

            # Safety for tiny widgets
            if width < 5 or height < 5:
                rel_x = width // 2
                rel_y = height // 2
            else:
                if rand_x > 0 or rand_y > 0 or (rand_x == 0 and rand_y == 0 and not (rand_x == 0 and rand_y == 0)):
                    # Prefer centered click with optional random offset when rand_x/rand_y provided
                    rel_x = width // 2
                    rel_y = height // 2
                    if rand_x > 0:
                        rel_x += random.randint(-rand_x, rand_x)
                    if rand_y > 0:
                        rel_y += random.randint(-rand_y, rand_y)
                else:
                    # Random behavior, avoiding edges
                    rel_x = random.randint(2, max(2, width - 3))
                    rel_y = random.randint(2, max(2, height - 3))

            # Clamp to stay safely inside (2px inset)
            rel_x = max(2, min(rel_x, width - 3))
            rel_y = max(2, min(rel_y, height - 3))

            abs_x = canvas_x + rel_x + rl_x
            abs_y = canvas_y + rel_y + rl_y

            for i in range(clicks):
                if i > 0 and sleep_interval != (0, 0):
                    time.sleep(random.uniform(sleep_interval[0], sleep_interval[1]))

                if action:
                    # Use select_menu_option logic for right-click + action
                    if select_menu_option(canvas_x + rel_x, canvas_y + rel_y, action):
                        return True
                    else:
                        return False
                elif right_click:
                    move(abs_x, abs_y, fast=fast, sleep=True, button='right')
                else:
                    move(abs_x, abs_y, fast=fast, sleep=True, button='left')
            return True

    return False

def click_widget_child(id_str, sprite_id=None, hidden=None, child_index=None, right_click=False, action=None, middle_point=True, rand_x=5, rand_y=5, clicks=1, sleep_interval=(0, 0), fast=False):
    """
    Clicks a child widget by parent ID and child_index (or falls back to any matching widget/child).
    - Defaults to reliable center click (+ small safe randomization).
    - Always clamps to stay strictly inside bounds (2px inset from edges).
    - No artificial +1 offset on canvas_x/y.
    - Supports right-click and action selection.
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

    # Find matching widgets (parent or child level)
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
            if widget.get("id") == widget_id and 'children' in widget:
                children = widget.get('children', [])
                if child_index < len(children):
                    candidate = children[child_index]
                    # Optional sprite check
                    if sprite_id is not None and candidate.get("spriteId") != sprite_id:
                        continue
                    if 'bounds' in candidate and candidate['bounds'].get('width', 0) > 0 and candidate['bounds'].get('height', 0) > 0:
                        target_widget = candidate
                        break
        if target_widget is None:
            print(f"No child widget at index {child_index} or invalid, falling back to first matching widget")
    
    # If no child match or no child_index, use first matching widget
    if target_widget is None and matching_widgets:
        target_widget = matching_widgets[0]

    if target_widget is None:
        print(f"No valid target widget found for ID {widget_id}" + (f", child_index {child_index}" if child_index is not None else ""))
        return False

    # Optional early return if already in desired sprite state
    if sprite_id is not None and target_widget.get("spriteId") == sprite_id:
        print(f"Target widget already has spriteId {sprite_id}")
        return True

    # Click logic
    if 'bounds' not in target_widget:
        print("Target widget has no bounds")
        return False

    bounds = target_widget['bounds']
    canvas_x = bounds['x']          # No +1 offset
    canvas_y = bounds['y']          # No +1 offset
    width = bounds['width']
    height = bounds['height']

    # Safety for tiny widgets
    if width < 5 or height < 5:
        print(f"Widget too small ({width}x{height}) - forcing exact center")
        rel_x = width // 2
        rel_y = height // 2
    else:
        if middle_point or rand_x > 0 or rand_y > 0:
            rel_x = width // 2
            rel_y = height // 2
            if rand_x > 0:
                rel_x += random.randint(-rand_x, rand_x)
            if rand_y > 0:
                rel_y += random.randint(-rand_y, rand_y)
        else:
            rel_x = random.randint(2, width - 3)
            rel_y = random.randint(2, height - 3)

    # CRITICAL: Clamp to stay safely inside (2px inset)
    rel_x = max(2, min(rel_x, width - 3))
    rel_y = max(2, min(rel_y, height - 3))

    abs_x = canvas_x + rel_x + rl_x
    abs_y = canvas_y + rel_y + rl_y

    print(f'click_widget_child: Clicking at screen ({abs_x}, {abs_y}) | Canvas ({canvas_x + rel_x}, {canvas_y + rel_y}) | '
          f'Bounds x={canvas_x}-{canvas_x + width - 1}, y={canvas_y}-{canvas_y + height - 1} '
          f'(child_index={child_index if child_index is not None else "N/A"})')

    for i in range(clicks):
        if i > 0 and sleep_interval != (0, 0):
            time.sleep(random.uniform(sleep_interval[0], sleep_interval[1]))

        if action:
            # Right-click + select action (reuse your existing select_menu_option if defined)
            # Replace with your actual function name
            if select_menu_option(canvas_x + rel_x, canvas_y + rel_y, action):
                return True
            return False
        elif right_click:
            move(abs_x, abs_y, fast=fast, sleep=True, button='right')
        else:
            move(abs_x, abs_y, fast=fast, sleep=True, button='left')

    return True


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

def click_widget_by_name(name_str, sprite_id=None, hidden=None, exact_match=False, child_index=None, right_click=False, action=None, middle_point=False, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0), canvas=None, fast=False):
    """
    Clicks a widget or child by name (case-insensitive partial or exact match), similar to click_widget.
    Now supports restricting search/clicks to a sub-area of the RuneLite client canvas.
    
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
        canvas (tuple, optional): (rel_x, rel_y, width, height) relative to RuneLite client canvas (0,0 top-left).
                                  None = full client area (default, from get_runelite_window_coords()).
                                  Only widgets whose bounds intersect this area are considered.
    
    Returns:
        bool: True if clicked successfully, False otherwise.
    """
    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data available")
        return False

    # Get RuneLite client position (screen) and size
    rl_x, rl_y = runelite_window(0, 0)
    full_coords = get_runelite_window_coords()
    if full_coords and len(full_coords) >= 4:
        _, _, canvas_w, canvas_h = full_coords
    else:
        canvas_w, canvas_h = 800, 600  # safe fallback

    # Resolve search canvas (relative to client canvas)
    if canvas is None:
        search_x = search_y = 0
        search_w = canvas_w
        search_h = canvas_h
    else:
        if len(canvas) != 4:
            print("canvas must be tuple (rel_x, rel_y, width, height)")
            return False
        search_x, search_y, search_w, search_h = [max(0, int(v)) for v in canvas]
        search_w = min(search_w, canvas_w - search_x)
        search_h = min(search_h, canvas_h - search_y)

    name_normalized = name_str.strip().lower()

    def strip_tags(text):
        """Remove all RuneScape-style tags like <col=ff9040>, </col>, <img=5>, etc."""
        if not text:
            return ""
        return re.sub(r'<[^>]*>', '', text).strip()

    def matches(widget):
        # Area filter first (intersection)
        if 'bounds' not in widget or not widget['bounds']:
            return False
        b = widget['bounds']
        wx = b.get('x', 0)
        wy = b.get('y', 0)
        ww = b.get('width', 0)
        wh = b.get('height', 0)
        if (wx + ww <= search_x or wx >= search_x + search_w or
            wy + wh <= search_y or wy >= search_y + search_h):
            return False

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

    # If child_index specified
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
        print(f"No widget found with plain name {match_type} '{name_str}' in area ({search_x},{search_y},{search_w},{search_h})")
        return False

    # Click logic (widget bounds always client-relative)
    if 'bounds' not in target_widget:
        print("Target widget has no bounds")
        return False

    bounds = target_widget['bounds']
    canvas_x = bounds['x'] + 1
    canvas_y = bounds['y'] + 1
    width = bounds['width']
    height = bounds['height']
    
    if middle_point:
        rel_x = width // 2
        rel_y = height // 2
        if rand_x > 0:
            rel_x += random.randint(-rand_x, rand_x)
        if rand_y > 0:
            rel_y += random.randint(-rand_y, rand_y)
        rel_x = max(1, min(rel_x, width - 2))
        rel_y = max(1, min(rel_y, height - 2))
    else:
        rel_x = random.randint(1, width - 2)
        rel_y = random.randint(1, height - 2)
    
    abs_x = canvas_x + rel_x + rl_x
    abs_y = canvas_y + rel_y + rl_y
    raw_name = target_widget.get("name", "")
    plain_name = strip_tags(raw_name)
    print(f'clicking widget by name at: {abs_x}, {abs_y} | area: ({search_x},{search_y},{search_w},{search_h}) | raw: "{raw_name}" -> plain: "{plain_name}"')
    
    for i in range(clicks):
        if i > 0 and sleep_interval != (0, 0):
            time.sleep(random.uniform(sleep_interval[0], sleep_interval[1]))
        
        if action:
            if select_menu_option(canvas_x + rel_x, canvas_y + rel_y, action):
                return True
            return False
        elif right_click:
            move(abs_x, abs_y, fast=fast, sleep=True, button='right')
        else:
            move(abs_x, abs_y, fast=fast, sleep=True, button='left')
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
# print(check_widget('35913796', sprite_id=1030))
# if not click_widget('35913795', sprite_id=1030, hidden=False, right_click=False, action=None, rand_x=0, rand_y=0, clicks=1, sleep_interval=(0, 0)):
#    exit(f'click widget 35913795 failed, exiting... time: {time.strftime("%H:%M:%S")}')
# click_widget_by_name("ring of wealth (5)", exact_match=True, canvas=(564, 217, 179, 250))