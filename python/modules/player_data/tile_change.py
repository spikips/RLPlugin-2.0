from modules.utils.wait_for_tick import wait_for_tick
from modules.core.plugin_client import player
import time

def wait_for_tile_change(timeout_ticks=20, max_retries=3):
    """
    Wait until the player's tile changes from the initial tile.
    
    Improvements:
    - Added retry mechanism for failed location fetches to handle transient errors.
    - Raises exceptions on persistent failures for better error propagation.
    - Returns True if changed, False on timeout.
    - Logs progress and errors for debugging.
    
    Parameters:
    - timeout_ticks: Max ticks to wait (default: 20).
    - max_retries: Max retries per location fetch (default: 3).
    
    From different views:
    - Reliability: Retries reduce flakiness in unstable environments.
    - Usability: Exceptions allow callers to handle errors (e.g., retry whole function or abort).
    - Performance: Minimal overhead; backoff could be added if needed for rate-limiting.
    - Bigger picture: This makes the function more robust for scripting in dynamic simulations/games where API calls might fail intermittently.
    """
    # Helper to fetch location with retries
    def get_location(retries=max_retries):
        for attempt in range(retries):
            data = player(location=True)
            if data and 'data' in data and 'location' in data['data']:
                return data['data']['location']
            print(f"Failed to get location (attempt {attempt + 1}/{retries}). Retrying...")
            time.sleep(0.1)  # Short backoff to avoid hammering
        raise ValueError("Persistent failure to fetch player location.")

    try:
        initial_tile = get_location()
        print(f"Initial location: {initial_tile}")
    except ValueError as e:
        print(f"Error getting initial location: {e}")
        raise  # Propagate to caller

    tick_count = 0
    while tick_count < timeout_ticks:
        try:
            current_tile = get_location()
            if current_tile != initial_tile:
                print(f"Tile changed from {initial_tile} to {current_tile} after {tick_count} ticks")
                return True
        except ValueError as e:
            print(f"Error during check: {e}. Continuing...")
        
        wait_for_tick()
        tick_count += 1

    print(f"Timeout after {timeout_ticks} ticks waiting for tile change")
    return False

# wait_for_tile_change()