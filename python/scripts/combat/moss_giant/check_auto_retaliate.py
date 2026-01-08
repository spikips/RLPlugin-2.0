import time
import pyautogui
from modules.widgets.widget_data import get_all_widget_data
from modules.core.mouse_control import move as mouse_click
from modules.core.window_utils import runelite_window, focus_runelite_window

def check_auto_retaliate(auto_retaliate: bool = None, widgets: list = None, leave_combat_tab_open=False):
    """
    Check and optionally toggle auto-retaliate, opening the combat tab if necessary.
    Returns to inventory tab (F1) after checking or toggling.
    
    Args:
        auto_retaliate (bool): True to enable, False to disable, None to ignore.
        widgets (list): Optional pre-fetched widget data to avoid re-fetching.
        leave_combat_tab_open (bool): If True, keeps combat tab open after execution.
    
    Returns:
        bool: True if auto-retaliate is in the desired state (or None if not toggling).
    """
    if auto_retaliate is None:
        return True  # No action needed
    
    auto_widget_id = 38862881
    on_sprite = 1150
    off_sprite = 1141
    open_tab = False

    # Ensure RuneLite window is focused
    focus_runelite_window()

    widgets = get_all_widget_data()
    for widget in widgets:
        if widget.get("id") == auto_widget_id:
            # Check first child's sprite for status
            if 'children' in widget and widget['children']:
                open_tab = True

    # Always open combat tab to ensure consistency
    if not open_tab:
        print("Opening combat tab for auto-retaliate")
        pyautogui.press('f3')
        time.sleep(0.1)  # Delay for tab switch

    # Fetch widget data after opening combat tab
    widgets = get_all_widget_data()
    if not widgets:
        print("Failed to retrieve widget data for auto-retaliate.")
        pyautogui.press('f1')  # Return to inventory
        time.sleep(0.2)
        return False


    desired_sprite = on_sprite if auto_retaliate else off_sprite

    for widget in widgets:
        if widget.get("id") == auto_widget_id:
            # Check first child's sprite for status
            if 'children' in widget and widget['children']:
                current_sprite = widget['children'][0].get('spriteId', -1)
                print(f"Auto-retaliate widget found. Current sprite: {current_sprite}, Desired sprite: {desired_sprite}")
                if current_sprite == desired_sprite:
                    print("Auto-retaliate is already in the desired state.")
                else:
                    if 'bounds' in widget:
                        bounds = widget['bounds']
                        canvas_x = bounds['x'] + bounds['width'] // 2
                        canvas_y = bounds['y'] + bounds['height'] // 2
                        screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                        mouse_click(screen_x, screen_y, button='left', fast=True, sleep=True)
                        time.sleep(0.1)  # Delay for click
                        print("Toggled auto-retaliate.")
                # Return to inventory tab unless specified otherwise
                if not leave_combat_tab_open:
                    pyautogui.press('f1')
                    time.sleep(0.2)
                return True
            else:
                print("Auto-retaliate widget has no children.")
            break

    print("Auto-retaliate widget not found.")
    # Return to inventory tab
    if not leave_combat_tab_open:
        pyautogui.press('f1')
        time.sleep(0.2)
    return False

# check_auto_retaliate(auto_retaliate=True, leave_combat_tab_open=True)