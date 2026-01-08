import time
import pyautogui 
from modules.core.plugin_client import combat_style as get_current_style
from modules.core.mouse_control import move as mouse_click
from modules.core.window_utils import focus_runelite_window, runelite_window
from modules.widgets.widget_data import get_all_widget_data

SLASH_SWORD_IDS = {
    'attack': 38862854,
    'strength': 38862858,
    'shared': 38862861,
    'defence': 38862866
}

BLUNT_WEAPON_IDS = {
    'attack': 38862854,
    'strength': 38862858,
    'defence': 38862866
}

STAB_SWORD_IDS = {
    'attack': 38862854,
    'strength': 38862858,  # Primary strength (lunge/aggressive stab)
    'aggressive_slash': 38862862,  # Secondary strength (slash aggressive)
    'defence': 38862865
}

def get_combat_styles(weapon_category: str = "slash weapon", desired_style: str = "attack"):
    """
    Ensure the desired combat style is active for the specified weapon category.
    Checks current style using plugin_client, opens tab only if change is needed.
    
    Args:
        weapon_category (str): Weapon category (e.g., "slash weapon", "blunt weapon", "stab weapon").
        desired_style (str): Desired style (e.g., "attack", "strength", "shared", "defence").
    
    Returns:
        dict: Final combat styles status after adjustment.
    """
    if weapon_category == "slash weapon":
        style_widgets = SLASH_SWORD_IDS
    elif weapon_category == "blunt weapon":
        style_widgets = BLUNT_WEAPON_IDS
    elif weapon_category == "stab weapon":
        style_widgets = STAB_SWORD_IDS
    else:
        print(f"Unsupported weapon category: {weapon_category}")
        return {}

    if desired_style not in style_widgets:
        print(f"Invalid desired style '{desired_style}' for {weapon_category}. Available styles: {list(style_widgets.keys())}")
        return {}

    # Focus RuneLite window
    if not focus_runelite_window():
        print("Failed to focus RuneLite window.")
        return {}

    # Get current style using plugin_client without opening tab
    current_response = get_current_style()
    current_style = current_response.get('data', {}).get('style', 'Unknown').lower() if current_response else 'Unknown'
    print(f"Current combat style: {current_style}, {current_response}")  # Debug

    # Check if change is needed
    if current_style == desired_style:
        print("Current style matches desired, no change needed.")
        return get_local_styles(style_widgets, weapon_category)

    # Open combat tab only if change required
    print('Opening combat tab for change')
    pyautogui.press('f3')
    time.sleep(0.1)  # Increased delay for tab switch reliability

    # Get widgets after opening tab
    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data retrieved. Plugin server may not be responding.")
        pyautogui.press('f1')
        time.sleep(0.2)
        return {}

    # Debug widget data for combat tab
    combat_tab_id = 35913791
    tab_open = False
    for widget in widgets:
        if widget.get("id") == combat_tab_id and widget.get("spriteId", -1) == 1026:
            tab_open = True
            print("Combat tab confirmed open (ID: 35913791, SpriteID: 1026)")
            break
    if not tab_open:
        print("Combat tab not open. Dumping widget IDs for debugging:")
        for widget in widgets:
            print(f"Widget ID: {widget.get('id')}, SpriteID: {widget.get('spriteId', -1), "combat_style.py"}")

    # Find and click the desired style widget
    for widget in widgets:
        if widget.get("id") == style_widgets[desired_style]:
            if 'bounds' in widget:
                bounds = widget['bounds']
                canvas_x = bounds['x'] + bounds['width'] // 2
                canvas_y = bounds['y'] + bounds['height'] // 2
                screen_x, screen_y = runelite_window(canvas_x, canvas_y)
                print(f"Clicking widget {style_widgets[desired_style]} at screen coordinates ({screen_x}, {screen_y})")
                mouse_click(screen_x, screen_y, button='left', fast=True)
                time.sleep(0.1)  # Delay for click
                break
            else:
                print(f"No bounds found for widget {style_widgets[desired_style]}")
                return {}


    # Verify and return final styles
    return get_local_styles(style_widgets, weapon_category)

def get_local_styles(style_widgets, weapon_category):
    """Local widget-based check for styles (tab must be open)."""
    widgets = get_all_widget_data()
    if not widgets:
        print("No widget data available for style check.")
        return {}

    combat_tab_id = 35913791
    tab_open = any(widget.get("id") == combat_tab_id and widget.get("spriteId", -1) == 1026 for widget in widgets)

    styles = {
        'tab_open': tab_open,
        'attack': 'disabled',
        'strength': 'disabled',
        'defence': 'disabled'
    }

    if weapon_category == "slash weapon":
        styles['shared'] = 'disabled'

    if not tab_open:
        print("Combat tab not open for style check.")
        return styles

    if weapon_category == "slash weapon":
        any_non_shared_enabled = False
        non_shared_keys = ['attack', 'strength', 'defence']
        for key in non_shared_keys:
            widget_id = style_widgets[key]
            for widget in widgets:
                if widget.get("id") == widget_id:
                    if 'children' in widget and widget['children']:
                        first_child_sprite = widget['children'][0].get('spriteId', -1)
                        if first_child_sprite == 1150:
                            styles[key] = 'enabled'
                            any_non_shared_enabled = True
                        elif first_child_sprite == 1141:
                            styles[key] = 'disabled'
                    break

        if not any_non_shared_enabled:
            styles['shared'] = 'enabled'
    elif weapon_category == "stab weapon":
        # Check attack and defence
        for key in ['attack', 'defence']:
            widget_id = style_widgets[key]
            for widget in widgets:
                if widget.get("id") == widget_id:
                    if 'children' in widget and widget['children']:
                        first_child_sprite = widget['children'][0].get('spriteId', -1)
                        if first_child_sprite == 1150:
                            styles[key] = 'enabled'
                        elif first_child_sprite == 1141:
                            styles[key] = 'disabled'
                    break

        # Check strength: enabled if either strength or aggressive_slash is enabled
        strength_enabled = False
        for str_key in ['strength', 'aggressive_slash']:
            widget_id = style_widgets[str_key]
            for widget in widgets:
                if widget.get("id") == widget_id:
                    if 'children' in widget and widget['children']:
                        first_child_sprite = widget['children'][0].get('spriteId', -1)
                        if first_child_sprite == 1150:
                            strength_enabled = True
                    break
        if strength_enabled:
            styles['strength'] = 'enabled'
    else:  # For blunt weapon, no shared
        for key in ['attack', 'strength', 'defence']:
            widget_id = style_widgets[key]
            for widget in widgets:
                if widget.get("id") == widget_id:
                    if 'children' in widget and widget['children']:
                        first_child_sprite = widget['children'][0].get('spriteId', -1)
                        if first_child_sprite == 1150:
                            styles[key] = 'enabled'
                        elif first_child_sprite == 1141:
                            styles[key] = 'disabled'
                    break

    print(f"Final styles: {styles}")  # Debug
    return styles

# get_combat_styles("slash weapon", "attack")
# get_combat_styles()