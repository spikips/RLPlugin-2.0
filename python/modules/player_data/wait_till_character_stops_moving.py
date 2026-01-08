from modules.core.plugin_client import player
from modules.utils.wait_for_tick import wait_for_tick

def wait_till_character_stopped_moving(max_ticks: int = 100, required_idle_ticks: int = 1):
    """
    Wait until the player has been idle (tile unchanged and animation idle) for the specified
    number of consecutive ticks.
    
    Args:
        max_ticks (int): Maximum number of ticks to wait before timing out (default: 100).
        required_idle_ticks (int): Number of consecutive idle ticks required before returning True
                                   (default: 1, preserves original behaviour).
    
    Returns:
        True if the player becomes idle for the required consecutive ticks within max_ticks,
        False otherwise.
    """
    if required_idle_ticks < 1:
        required_idle_ticks = 1
    
    attempt = 0
    consecutive_idle = 0
    
    while attempt < max_ticks:
        pl_data = player(location=True, animation=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data'] or 'animation' not in pl_data['data']:
            print("Failed to fetch player location or animation")
            return False
        
        initial_loc = pl_data['data']['location']
        initial_tile = (initial_loc['x'], initial_loc['y'], initial_loc['plane'])
        
        wait_for_tick(ticks=1)
        
        pl_data = player(location=True, animation=True)
        if not pl_data or 'data' not in pl_data or 'location' not in pl_data['data']:
            print("Failed to fetch player location after tick")
            return False
        
        current_loc = pl_data['data']['location']
        current_tile = (current_loc['x'], current_loc['y'], current_loc['plane'])
        animation = pl_data['data']['animation']
        
        is_idle = current_tile == initial_tile and animation in [0, -1]
        print(f"Player idle check (attempt {attempt + 1}): Tile unchanged: {current_tile == initial_tile}, "
              f"Animation: {animation}, Idle: {is_idle}, Consecutive: {consecutive_idle + 1 if is_idle else 0}")
        
        if is_idle:
            consecutive_idle += 1
            if consecutive_idle >= required_idle_ticks:
                return True
        else:
            consecutive_idle = 0
        
        attempt += 1
    
    print(f"Timeout: Player did not become idle for {required_idle_ticks} consecutive tick(s) after {max_ticks} ticks")
    return False

# wait_till_character_stopped_moving(required_idle_ticks=2)
# wait_till_character_stopped_moving()