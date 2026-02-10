# Add this to a utils file (e.g., player_status.py) or your main script

from modules.core.plugin_client import get_var
from modules.utils.wait_for_tick import wait_for_next_tick

def is_poisoned() -> bool:
    """
    Check if the player is poisoned by querying Var ID 102.
    
    Poisoned: Varp value > 0
    Not poisoned: Varp value == 0
    
    Returns:
        bool: True if poisoned, False otherwise (or if query fails).
    """
    result = get_var(102)
    if not result:
        print("Failed to query Var 102 (poison check)")
        return False
    
    # Navigate the nested 'data' structure
    try:
        inner_data = result.get('data', {})
        if isinstance(inner_data, dict):
            values_data = inner_data.get('data', {})
        else:
            values_data = inner_data  # In case structure varies
        
        values = values_data.get('values', {})
        varp_value = values.get('varp', 0)
        
        poisoned = varp_value > 0
        print(f"Poison check (Var 102): Varp = {varp_value} -> Poisoned = {poisoned}")
        return poisoned
    except Exception as e:
        print(f"Error parsing poison check response: {e}")
        print(f"Raw response: {result}")
        return False

# # === Usage Example ===
# while True:
#     if is_poisoned():
#         print("Player is poisoned - drink anti-poison!")
#     else:
#         print("Player is not poisoned")
#     wait_for_next_tick()