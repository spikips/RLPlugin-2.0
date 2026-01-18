# Updated varbit_change.py to handle the new change formats with 'type'

from modules.core.plugin_client import varbit_changes
import time

def varbit_change():
    response = varbit_changes()
    # print(response)
    if response and 'data' in response:
        changes = response['data']
        for change in changes:
            change_type = change.get('type', 'unknown')
            old_val = change['old'] if change['old'] != -1 else 'unknown'
            new_val = change['new']
            tick = change['tick']
            if change_type == 'varbit':
                print(f"Varbit {change['id']} changed: {old_val} -> {new_val} (tick {tick})")
            elif change_type == 'varp':
                print(f"Varp (Varplayer) {change['id']} changed: {old_val} -> {new_val} (tick {tick})")
            elif change_type == 'varclientint':
                print(f"VarClientInt {change['id']} changed: {old_val} -> {new_val} (tick {tick})")
            else:
                print(f"Unknown change type {change_type}: {change}")
    print('-\n')
    time.sleep(0.6)  # Tick sync