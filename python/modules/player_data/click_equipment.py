# click_equipment.py
"""
Module for clicking equipped items by name and selecting a menu action.
Usage: Import and call click_equipment_item(item_name, action).
Example: click_equipment_item("Ring of dueling", "Ferox Enclave")
"""

from modules.core.plugin_client import gear
from modules.widgets.widget import check_widget_name, click_widget
from modules.core.window_utils import focus_runelite_window

EQUIPMENT_WIDGET_IDS = [
    25362447, 25362448, 25362449, 25362450, 25362451,
    25362452, 25362453, 25362454, 25362455, 25362456, 25362457
]

def click_equipment_item(item_name: str, action: str = None, right_click: bool = False):
    """
    Clicks an equipped item by partial name match and optionally selects a menu action.
    
    Args:
        item_name (str): Partial name of the equipped item (case-insensitive, e.g., "Ring of dueling").
        action (str, optional): Menu action to select after right-click (e.g., "Ferox Enclave"). If provided, performs right-click + select.
        right_click (bool): If True and no action, just right-clicks the item.
    
    Returns:
        bool: True if successful (item found and clicked), False otherwise.
    """
    focus_runelite_window()  # Ensure RuneLite is focused
    
    # Optional: Confirm item is equipped via gear()
    gear_data = gear()
    equipped = False
    if gear_data and 'data' in gear_data:
        for equipped_name in gear_data['data'].keys():
            if item_name.lower() in equipped_name.lower():
                equipped = True
                print(f"Confirmed {equipped_name} is equipped.")
                break
    
    if not equipped:
        print(f"No equipped item matching '{item_name}' found via gear check.")
        return False
    
    # Loop through equipment widget IDs
    for widget_id in EQUIPMENT_WIDGET_IDS:
        widget_name = check_widget_name(str(widget_id))
        if widget_name and item_name.lower() in widget_name.lower():
            print(f"Found matching item '{widget_name}' at widget ID {widget_id}.")
            
            # Click with action or right-click
            if action:
                success = click_widget(str(widget_id), action=action)
            else:
                success = click_widget(str(widget_id), right_click=right_click)
            
            if success:
                print(f"Successfully interacted with '{widget_name}' using action '{action}'.")
                return True
            else:
                print(f"Failed to interact with '{widget_name}'.")
                return False
    
    print(f"No widget found for equipped item matching '{item_name}'.")
    return False

# Example usage (can be run directly)
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python click_equipment.py <item_name> [action]")
        sys.exit(1)
    
    item_name = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else None
    
    click_equipment_item(item_name, action)


# click_equipment_item('staff of air', action='examine')
