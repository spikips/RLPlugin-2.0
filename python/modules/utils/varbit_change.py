# varbit_change.py - Updated to monitor specific Varbit/Varp/VarClientInt IDs
# Prints changes only for the specified ID(s), regardless of type (varbit, varp, varclientint)

from modules.core.plugin_client import varbit_changes
import time

def monitor_var_changes(target_ids, poll_interval=0.6):
    """
    Continuously monitor for changes to specific Var change IDs.
    
    Args:
        target_ids (int or list[int]): Single ID or list of IDs to monitor.
        poll_interval (float): Sleep time between polls (default ~1 tick).
    """
    if isinstance(target_ids, int):
        target_ids = [target_ids]
    target_ids = set(target_ids)  # Fast lookup
    
    print(f"Monitoring changes for ID(s): {', '.join(map(str, target_ids))}")
    print("-" * 50)
    
    while True:
        response = varbit_changes()
        if response and 'data' in response:
            changes = response['data']
            relevant_changes = [
                change for change in changes
                if change['id'] in target_ids
            ]
            
            for change in relevant_changes:
                change_id = change['id']
                change_type = change.get('type', 'unknown')
                old_val = change['old'] if change['old'] != -1 else 'unknown'
                new_val = change['new']
                tick = change['tick']
                
                type_label = change_type.capitalize() if change_type != 'unknown' else 'Var'
                print(f"{type_label} {change_id} changed: {old_val} -> {new_val} (tick {tick})")
        
        if not response or not response.get('data'):
            print("No changes this tick")
        
        print('-')
        time.sleep(poll_interval)

# === Usage Examples ===

# Monitor a single ID (e.g., 12391)
monitor_var_changes(102)

# Monitor multiple IDs
# monitor_var_changes([12391, 12392, 3079])

# Or run with a single ID
# monitor_var_changes(12391)