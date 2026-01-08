from modules.utils.wait_for_tick import wait_for_tick
from modules.core.plugin_client import player
import time

def wait_until_stopped(timeout_ticks=30, confirm_ticks=2, max_retries=3):
    """
    Wait until the player's location (tile) has remained unchanged for the specified number of consecutive ticks,
    indicating the character has stopped moving. This is useful after issuing a movement command to ensure
    the player has reached the destination and is idle.
    
    Improvements over basic polling:
    - Uses a confirmation counter to avoid false positives from single-tick lags.
    - Incorporates retry logic for location fetches to handle API flakiness.
    - Includes timeout to prevent infinite loops in edge cases (e.g., stuck player).
    - Logs progress, changes, and errors for debugging.
    
    Parameters:
    - timeout_ticks: Maximum total ticks to monitor before timing out (default: 30, ~18s at 0.6s/tick).
    - confirm_ticks: Number of consecutive unchanged ticks required to confirm stopped (default: 2).
    - max_retries: Max retries per location fetch (default: 3).
    
    Returns:
    - bool: True if stopped within timeout, False on timeout.
    
    Raises:
    - ValueError: If initial location fetch fails persistently.
    
    Example Usage:
    # After clicking to move somewhere
    if wait_until_stopped():
        print("Player has stopped moving.")
    else:
        print("Player did not stop within timeout; may be stuck.")
    """
    # Helper to fetch location with retries (reused from wait_for_tile_change)
    def get_location(retries=max_retries):
        for attempt in range(retries):
            data = player(location=True)
            if data and 'data' in data and 'location' in data['data']:
                return data['data']['location']
            print(f"Failed to get location (attempt {attempt + 1}/{retries}). Retrying...")
            time.sleep(0.1)  # Short backoff
        raise ValueError("Persistent failure to fetch player location.")

    try:
        previous_tile = get_location()
        print(f"Initial location (monitoring for stop): {previous_tile}")
    except ValueError as e:
        print(f"Error getting initial location: {e}")
        raise  # Propagate to caller

    consecutive_same = 1  # Start with 1 since we have the initial
    tick_count = 0

    while tick_count < timeout_ticks:
        wait_for_tick()
        tick_count += 1

        try:
            current_tile = get_location()
            if current_tile != previous_tile:
                print(f"Location changed from {previous_tile} to {current_tile} at tick {tick_count}; resetting stop counter.")
                previous_tile = current_tile
                consecutive_same = 1  # Reset on movement
            else:
                consecutive_same += 1
                print(f"Location unchanged at {current_tile} for {consecutive_same} consecutive ticks (tick {tick_count}).")

            # Check if we've confirmed stopped
            if consecutive_same >= confirm_ticks:
                print(f"Player confirmed stopped at {current_tile} after {tick_count} total ticks ({consecutive_same} unchanged).")
                return True

        except ValueError as e:
            print(f"Error during location check at tick {tick_count}: {e}. Skipping this tick...")

    print(f"Timeout after {timeout_ticks} ticks without confirming stop (last at {consecutive_same} unchanged ticks).")
    return False

# wait_until_stopped()  # Uncomment to test