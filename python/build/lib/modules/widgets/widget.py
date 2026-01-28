import random
from time import time
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window

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

def click_widget(id_str, sprite_id=None, hidden=False):
    rl_x, rl_y = runelite_window(0, 0)
    try:
        widget_id = int(id_str)
    except ValueError:
        return False

    widgets = get_all_widget_data()
    # print(widgets)
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
            # print(f'widget clicking at: {random_x}, {random_y}, canvas: {canvas_x}, {canvas_y}, width: {width}, height: {height}')
            
            move(random_x, random_y, fast=True, sleep=True, button='left')
            return True

    return False

def click_widget_child(id_str, sprite_id=None, hidden=None, child_index=None):
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

    print(f"Clicking at coordinates: ({random_x}, {random_y})")
    move(random_x, random_y, fast=True, sleep=True, button='left')
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

# Example usage for debugging
# while True:
# click_widget(35913778)

# print(click_widget_child('8454157', child_index=1))
# print(click_widget('35913795', sprite_id=1030))
# click_widget('8454150')
# print(check_widget('8454157', sprite_id=699, child_index=100))
# print(check_widget('35913795', sprite_id=1030))
# print(check_widget_text('8454157', child_index=1))
# print(check_widget('8454157', child_index=4, sprite_id=699))
