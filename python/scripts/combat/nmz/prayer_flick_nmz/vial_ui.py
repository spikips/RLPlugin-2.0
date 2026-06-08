# vial_ui.py
from modules.widgets.widget import check_widget, check_widget_text, click_widget_child, click_widget
from modules.player_data.tile_change import wait_for_tile_change
from modules.utils.wait_for_tick import wait_for_tick
import json
import os
import time

def boss_config():
    """
    Configure the NMZ vial UI by enabling specified bosses from config.json and disabling others.
    Assumes the vial UI widget '8454146' is open.
    
    Returns:
    bool: True if configuration succeeded, False otherwise.
    """
    # Check if vial UI is open
    if not check_widget('8454146'):
        print("Vial UI widget '8454146' not found or not open.")
        return False
    
    # Get absolute path to config.json in the script's directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    
    # Load enabled bosses list from config.json
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            enabled_bosses = config.get('bosses', [])
            # Normalize to lowercase
            enabled_bosses = [boss.lower() for boss in enabled_bosses]
    except FileNotFoundError:
        print(f"{json_path} not found.")
        return False
    except json.JSONDecodeError:
        print("Invalid JSON in config.json.")
        return False
    
    # Loop over boss blocks (groups of 3 children: name at n, button at n+1, useless at n+2)
    success = True
    child_index = 1  # Starting index for first boss name
    while True:
        try:
            text = check_widget_text('8454157', child_index=child_index)
        except Exception as e:
            print(f"End of boss list reached at child_index {child_index}: {e}")
            break
        if text is None:
            print(f"End of boss list reached at child_index {child_index} (text None)")
            break
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
    start_time = time.time()
    result = boss_config()
    end_time = time.time()
    execution_time = end_time - start_time
    print(f"Script execution time: {execution_time:.2f} seconds")
    print(result)