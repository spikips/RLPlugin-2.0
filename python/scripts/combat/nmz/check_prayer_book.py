import random
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move as mouse_click
from modules.core.window_utils import runelite_window

def check_prayer_spellbook():
    """
    Check if the prayer spellbook is open (Id: 35913796, SpriteId: 1030 when open, -1 when closed).
    Opens the spellbook if it's not open by clicking a random point inside its bounds.
    
    Returns:
        bool: True if spellbook is open or successfully opened, False otherwise.
    """
    # Get all widget data
    widgets = get_all_widget_data()
    if not widgets:
        print("Failed to retrieve widget data.")
        return False

    # Check if prayer spellbook widget is open
    spellbook_open = any(widget.get("id") == 35913796 and widget.get("spriteId") == 1030 for widget in widgets)
    if spellbook_open:
        print("Prayer spellbook is already open.")
        return True

    # If not open, find the widget and click a random point inside its bounds
    print("Prayer spellbook is closed, attempting to open...")
    for widget in widgets:
        if widget.get("id") == 35913796 and widget.get("spriteId") == -1:
            if 'bounds' in widget:
                bounds = widget['bounds']
                canvas_x = bounds['x']
                canvas_y = bounds['y']
                width = bounds['width']
                height = bounds['height']
                
                # Generate random coordinates within the widget bounds
                random_x = canvas_x + random.randint(5, width - 5)
                random_y = canvas_y + random.randint(5, height - 5)
                
                print('opening prayer book')
                # Convert to screen coordinates
                screen_x, screen_y = runelite_window(random_x, random_y)
                mouse_click(screen_x, screen_y, button='left')
                
                # Verify it opened
                widgets = get_all_widget_data()
                if any(w.get("id") == 35913796 and w.get("spriteId") == 1030 for w in widgets):
                    print(f"Successfully opened prayer spellbook by clicking at ({random_x}, {random_y}).")
                    return True
                else:
                    print("Failed to open prayer spellbook.")
                    return False
    print("Prayer spellbook widget not found.")
    return False
