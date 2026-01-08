from modules.widgets.widget import check_widget, check_widget_text, click_widget_child, click_widget
from modules.utils.wait_for_tick import wait_for_tick
from modules.player_data.tile_change import wait_for_tile_change
import json
import os

def boss_config():
    """
    Configure the NMZ vial UI by enabling specified bosses from boss_config.json and disabling others.
    Assumes the vial UI widget '8454146' is open.
    
    Returns:
    bool: True if configuration succeeded, False otherwise.
    """
    # Check if vial UI is open
    if not check_widget('8454146'):
        print("Vial UI widget '8454146' not found or not open.")
        return False
    
    # Get absolute path to boss_config.json in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'boss_config.json')
    
    # Load enabled bosses list from boss_config.json
    try:
        with open(json_path, 'r') as f:
            enabled_bosses = json.load(f)
            # Normalize to lowercase
            enabled_bosses = [boss.lower() for boss in enabled_bosses]
    except FileNotFoundError:
        print(f"{json_path} not found.")
        return False
    except json.JSONDecodeError:
        print("Invalid JSON in boss_config.json.")
        return False
    
    # Loop over boss blocks (groups of 3 children: name at n, button at n+1, useless at n+2)
    success = True
    child_index = 1  # Starting index for first boss name
    while True:
        text = check_widget_text('8454157', child_index=child_index)
        if text is None:
            break  # End of children
        boss_name = text.lower()
        desired_enabled = boss_name in enabled_bosses
        # Check button state (sprite_id=699 for enabled, at child_index+1)
        is_enabled = check_widget('8454157', sprite_id=699, child_index=child_index + 1)
        if is_enabled != desired_enabled:
            print(f"{'Enabling' if desired_enabled else 'Disabling'} '{text}' by clicking child_index {child_index}.")
            if not click_widget_child('8454157', child_index=child_index):
                print(f"Failed to toggle '{text}'.")
                success = False
        else:
            print(f"'{text}' is already {'enabled' if is_enabled else 'disabled'}.")
        
        # Move to next boss block
        child_index += 3
    
    wait_for_tick(2)
    click_widget('8454150')

    if wait_for_tile_change():
        return success
    return False

if __name__ == "__main__":
    print(boss_config())