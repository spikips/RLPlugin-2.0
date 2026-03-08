from modules.core.plugin_client import player
from modules.utils.wait_for_tick import wait_for_tick

from modules.core.plugin_client import player
from modules.utils.wait_for_tick import wait_for_tick

def wait_till_character_stopped_moving(max_ticks: int = 100, required_idle_ticks: int = 1):
    """
    Wait until the player's tile has been unchanged for the specified number of consecutive ticks.
    This detects when pathing/movement has stopped (tile stable), ignoring ongoing animations.
    
    Args:
        max_ticks (int): Maximum ticks to wait before timeout (default: 100).
        required_idle_ticks (int): Consecutive ticks with unchanged tile to consider "stopped" (default: 3).
                                   Use 3+ to avoid false positives from brief pauses (recommended).
                                   Set to 1 for faster but potentially less reliable detection.
    
    Returns:
        bool: True if stopped within max_ticks, False on timeout/no data.
    """
    if required_idle_ticks < 1:
        required_idle_ticks = 1
    
    attempt = 0
    consecutive_idle = 0
    
    while attempt < max_ticks:
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location")
            wait_for_tick(ticks=1)
            attempt += 1
            continue
        
        initial_loc = pl_data['data']['location']
        initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
        
        wait_for_tick(ticks=1)
        
        pl_data = player(location=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location after tick")
            consecutive_idle = 0  # Reset on error
            attempt += 1
            continue
        
        current_loc = pl_data['data']['location']
        current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
        
        tile_unchanged = current_tile == initial_tile
        print(f"Idle check (attempt {attempt + 1}): Tile unchanged: {tile_unchanged}, "
              f"Consecutive idle: {consecutive_idle + 1 if tile_unchanged else 0}")
        
        if tile_unchanged:
            consecutive_idle += 1
            if consecutive_idle >= required_idle_ticks and attempt != 0:
                print(f"Character stopped moving (tile stable for {required_idle_ticks} ticks)")
                return True
        else:
            consecutive_idle = 0
        
        attempt += 1
    
    print(f"Timeout: Character did not stop moving after {max_ticks} ticks")
    return False

# wait_till_character_stopped_moving(required_idle_ticks=2)
# wait_till_character_stopped_moving()