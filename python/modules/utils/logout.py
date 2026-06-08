import time
import random
from datetime import datetime, timedelta
from modules.core.plugin_client import game_state, inventory
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window
from modules.widgets.widget import click_widget

rl_x, rl_y = runelite_window(0, 0)


def is_in_inactive_period(current_hour, inactive_start, inactive_end):
    """Returns True if current hour is inside the inactive (sleep) window."""
    if inactive_start < inactive_end:
        return inactive_start <= current_hour < inactive_end
    # Overnight case (e.g. 22 → 7)
    return current_hour >= inactive_start or current_hour < inactive_end


def get_seconds_until_active(inactive_start, inactive_end, randomize_hours=1):
    """Calculates how many seconds to wait until we are outside the inactive window + randomization."""
    now = datetime.now()
    hour = now.hour

    if not is_in_inactive_period(hour, inactive_start, inactive_end):
        return 0  # already in active hours → log in immediately

    # Target = end of inactive period (tomorrow if we're in the evening)
    if now.hour >= inactive_start:
        target = (now + timedelta(days=1)).replace(
            hour=inactive_end, minute=0, second=0, microsecond=0
        )
    else:
        target = now.replace(
            hour=inactive_end, minute=0, second=0, microsecond=0
        )

    # Apply ± randomize_hours on the boundary
    rand_offset = random.uniform(-randomize_hours, randomize_hours)
    target += timedelta(hours=rand_offset)

    # Make sure it's in the future
    if target <= now:
        target += timedelta(days=1)

    wait_seconds = (target - now).total_seconds()
    return max(wait_seconds, 60)  # at least 1 minute


def logout_and_break(break_minutes, inactive_start=22, inactive_end=7, randomize_hours=1):
    """Logout, take a break, and only log back in outside the inactive window (with randomization)."""
    print("Initiating logout for break")
    logged_out = False

    # clicks logout widget
    click_widget(35913786, rand_x=10, rand_y=10)

    time.sleep(random.uniform(0.22, 2.55))
    tries = 0
    while not logged_out:
        # Logout clicks
        logout_1 = click_widget(11927564)
        if not logout_1:
            click_widget(4522009)

        # Poll for up to 2 seconds
        start_poll = time.time()
        while time.time() - start_poll < 2:
            if game_state().get('data') == "LOGIN_SCREEN":
                print("Logged out successfully")
                logged_out = True
                break
            time.sleep(0.1)

        if not logged_out:
            tries += 1
            print(f"Logout not detected, retrying... (try {tries})")

    # === Minimum break ===
    break_seconds = break_minutes * 60
    start_time = datetime.now()
    resume_time = start_time + timedelta(seconds=break_seconds)
    duration = timedelta(seconds=break_seconds)
    print(f"Break started at: {start_time.strftime('%H:%M:%S')}")
    print(f"Script will resume at: {resume_time.strftime('%H:%M:%S')} (minimum)")
    print(f"Base sleep duration: {str(duration).split('.')[0]}")

    time.sleep(break_seconds)

    # === NEW: Respect inactive / sleep hours ===
    additional_wait = get_seconds_until_active(inactive_start, inactive_end, randomize_hours)
    if additional_wait > 0:
        additional_duration = timedelta(seconds=additional_wait)
        actual_resume = datetime.now() + additional_duration
        print(f"Current time is inside inactive window ({inactive_start}:00–{inactive_end}:00).")
        print(f"Additional wait: {str(additional_duration).split('.')[0]}")
        print(f"Will log back in around: {actual_resume.strftime('%H:%M:%S')}")
        time.sleep(additional_wait)

    # === Login sequence (same as before) ===
    print("Performing login sequence...")
    mouse(391 + rl_x, 303 + rl_y, button="left")
    time.sleep(random.uniform(0.22, 0.3))
    mouse(391 + rl_x, 263 + rl_y, button="left")

    # Poll for login states, up to 15 seconds total
    start_time_poll = time.time()
    first_logged_in = False
    while time.time() - start_time_poll < 15:
        state = game_state().get('data')
        print(f"Main Menu Data: {{'data': '{state}'}}")
        if state == 'LOGGED_IN' and not first_logged_in:
            time.sleep(0.4)   # Wait 0.4s before click
            mouse(400 + rl_x, 343 + rl_y, button="left")
            time.sleep(0.6)   # Wait 0.6s after click
            print("Clicked post-login button after first LOGGED_IN")
            first_logged_in = True
            return True
        time.sleep(0.1)
    print("Login timed out after 15 seconds")
    exit("Failed to log back in")


def check_login_state_and_login():
    """(unchanged - kept original behaviour)"""
    if game_state().get('data') == "LOGIN_SCREEN":
        mouse(391 + rl_x, 303 + rl_y, button="left")
        time.sleep(random.uniform(0.22, 0.3))
        mouse(391 + rl_x, 263 + rl_y, button="left")

        start_time_poll = time.time()
        first_logged_in = False
        while time.time() - start_time_poll < 15:
            state = game_state().get('data')
            print(f"Main Menu Data: {{'data': '{state}'}}")
            if state == 'LOGGED_IN' and not first_logged_in:
                time.sleep(0.6)
                mouse(400 + rl_x, 343 + rl_y, button="left")
                time.sleep(0.65)
                print("Clicked post-login button after first LOGGED_IN")
                first_logged_in = True
                return True
            time.sleep(0.1)
        print("Login timed out after 15 seconds")
        exit("Failed to log back in")
    return False


def logout():
    """(unchanged)"""
    print("Initiating logout")
    logged_out = False

    click_widget(35913786, rand_x=10, rand_y=10)

    time.sleep(random.uniform(0.22, 0.25))
    tries = 0
    while not logged_out:
        logout_1 = click_widget(11927564)
        if not logout_1:
            click_widget(4522009)

        start_poll = time.time()
        while time.time() - start_poll < 2:
            if game_state().get('data') == "LOGIN_SCREEN":
                print("Logged out successfully")
                logged_out = True
                break
            time.sleep(0.1)

        if not logged_out:
            tries += 1
            print(f"Logout not detected, retrying... {tries}")


# Example calls (uncomment the one you want)
# logout_and_break(69, inactive_start=22, inactive_end=7, randomize_hours=1)
# check_login_state_and_login()
# logout()