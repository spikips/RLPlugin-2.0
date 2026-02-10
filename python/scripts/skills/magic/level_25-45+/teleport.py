import time, random
from modules.utils.wait_for_tick import wait_for_tick
from modules.widgets.widget import check_widget, click_widget
from modules.core.plugin_client import stats, game_state
from modules.core.window_utils import focus_runelite_window
from modules.utils.logout import check_login_state_and_login, logout


def get_magic_level_from_stats(stats_dict):
    """Return the player's Magic level from the stats dict or None on failure."""
    try:
        return int(stats_dict['Magic']['level'])
    except Exception as e:
        print('Could not read Magic level from stats:', e)
        return None


def magic_spell_widget_for_level(level):
    """Map a Magic level to the appropriate teleport widget ID.

    Ranges (from repo comments):
    - 25-30 -> '14286871'
    - 31-36 -> '14286874'
    - 37-44 -> '14286877'
    - 45+   -> '14286882'
    Returns the widget id string or None if no mapping.
    """
    if level is None:
        return None
    if 25 <= level <= 30:
        return '14286871'
    if 31 <= level <= 36:
        return '14286874'
    if 37 <= level <= 44:
        return '14286877'
    if level >= 45:
        return '14286882'
    return None


def check_login_status():
    """Check if the player is logged in. Returns True if logged in, False otherwise."""
    try:
        state = game_state()['data']
        is_logged_in = state == 'LOGGED_IN'
        print(f'Game state: {state}')
        return is_logged_in
    except Exception as e:
        print(f'Could not check login status: {e}')
        return False


def handle_login():
    """Handle login if not already logged in."""
    if not check_login_status():
        print('Not logged in. Attempting to log in...')
        if check_login_state_and_login():
            print('Successfully logged in.')
            time.sleep(2)  # Wait for game to fully load
        else:
            print('Failed to log in. Exiting.')
            exit()
    else:
        print('Already logged in.')


def choose_and_cast_teleport(ensure_tab=True):
    """Choose the teleport widget for the player's Magic level and cast.

    - ensure_tab: if True, ensure the Magic tab is open before clicking

    Returns: (level, widget_id, clicked_bool)
    """
    level = get_magic_level_from_stats(stats()['data'])
    widget = magic_spell_widget_for_level(level)
    if widget is None:
        print(f'No teleport widget mapped for Magic level: {level}')
        exit()

    print(f'Magic level: {level} -> teleport widget: {widget}')

    # Ensure the magic tab is open (widget id and sprite check taken from this file comments)
    if ensure_tab and not check_widget('35913798', sprite_id=1027):
        click_widget('35913798', rand_x=10, rand_y=10)
        # small wait for tab to open
        for _ in range(50):
            if check_widget('35913798', sprite_id=1027):
                break
            time.sleep(0.05)

    # perform the click (left-click by default)
    click_widget(widget)
    wait_for_tick(4)
    if random.randint(0, 100) == 0:
        wait_ticks = random.randint(1, 50)
        print('Random extra wait for', wait_ticks, 'ticks')
        wait_for_tick(wait_ticks)
    
    return level


def start_teleporting(target_level=None):
    """Start the teleporting script.
    
    Args:
        target_level: Stop at this Magic level. If None, runs indefinitely.
    """
    handle_login()
    focus_runelite_window()
    
    print(f'Starting teleport script. Target level: {target_level if target_level else "No limit"}')
    
    try:
        while True:
            if not check_login_status():
                # logged out -> wait 45-90 minutes then attempt to login
                wait_minutes = random.randint(45, 90)
                print(f'Logged out detected. Waiting {wait_minutes} minutes before attempting re-login.')
                time.sleep(wait_minutes * 60)
                print('Attempting re-login now...')
                if check_login_state_and_login():
                    print('Re-login successful.')
                    time.sleep(2)
                    focus_runelite_window()
                else:
                    print('Re-login attempt failed; will retry after 30s.')
                    time.sleep(30)
                    continue

            current_level = choose_and_cast_teleport()
            
            # Check if we've reached the target level
            if target_level and current_level >= target_level:
                print(f'Reached target Magic level {target_level}. Logging out and stopping.')
                try:
                    logout()
                except Exception as e:
                    print('Logout failed:', e)
                break

            # short randomized pause between casts
            time.sleep(random.uniform(0.5, 1.5))
    except KeyboardInterrupt:
        print('Script stopped by user.')

# Example usage:
# start_teleporting(target_level=45)  # Stop at level 45
# start_teleporting()  # Run indefinitely
if __name__ == '__main__':
    start_teleporting(target_level=75)