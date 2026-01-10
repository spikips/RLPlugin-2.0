import time
import random
from datetime import datetime, timedelta
from modules.core.plugin_client import game_state
from modules.core.mouse_control import move as mouse
from modules.core.window_utils import runelite_window
from modules.widgets.widget import click_widget

rl_x, rl_y = runelite_window(0, 0)

def check_login_state_and_login():
    """Check login state and perform login sequence if at login screen."""
    if game_state().get('data') == "LOGIN_SCREEN":
        mouse(391 + rl_x, 303 + rl_y, button="left", fast=True, sleep=True)
        time.sleep(random.uniform(0.22, 0.3))
        mouse(391 + rl_x, 263 + rl_y, button="left", fast=True, sleep=True)

        # Poll for login states, up to 15 seconds total
        start_time_poll = time.time()
        first_logged_in = False
        while time.time() - start_time_poll < 15:
            state = game_state().get('data')
            print(f"Main Menu Data: {{'data': '{state}'}}")
            if state == 'LOGGED_IN' and not first_logged_in:
                time.sleep(0.4)  # Wait 0.4s before click
                mouse(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
                time.sleep(0.6)  # Wait 0.6s after click
                print("Clicked post-login button after first LOGGED_IN")
                first_logged_in = True
                return True  # Exit early after successful login and clicks
            time.sleep(0.1)
        print("Login timed out after 15 seconds")
        exit("Failed to log back in")
    return False

def logout_and_break(break_minutes):
    """Logout, take a break for specified minutes, and log back in. Prints timestamps and duration."""
    print("Initiating logout for break")
    logged_out = False

    # clicks logout widget
    click_widget(35913786, rand_x=10, rand_y=10)

    time.sleep(random.uniform(0.22, 0.25))
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
            print(f"Logout not detected, retrying...", {tries})

    # Calculate and print times
    break_seconds = break_minutes * 60
    start_time = datetime.now()
    resume_time = start_time + timedelta(seconds=break_seconds)
    duration = timedelta(seconds=break_seconds)
    print(f"Break started at: {start_time.strftime('%H:%M:%S')}")
    print(f"Script will resume at: {resume_time.strftime('%H:%M:%S')}")
    print(f"Sleep duration: {str(duration).split('.')[0]}")  # hh:mm:ss format

    time.sleep(break_seconds)

    mouse(391 + rl_x, 303 + rl_y, button="left", fast=True, sleep=True)
    time.sleep(random.uniform(0.22, 0.3))
    mouse(391 + rl_x, 263 + rl_y, button="left", fast=True, sleep=True)

    # Poll for login states, up to 15 seconds total
    start_time_poll = time.time()
    first_logged_in = False
    while time.time() - start_time_poll < 15:
        state = game_state().get('data')
        print(f"Main Menu Data: {{'data': '{state}'}}")
        if state == 'LOGGED_IN' and not first_logged_in:
            time.sleep(0.4)  # Wait 0.4s before click
            mouse(400 + rl_x, 343 + rl_y, button="left", fast=True, sleep=True)
            time.sleep(0.6)  # Wait 0.6s after click
            print("Clicked post-login button after first LOGGED_IN")
            first_logged_in = True
            return True  # Exit early after successful login and clicks
        time.sleep(0.1)
    print("Login timed out after 15 seconds")
    exit("Failed to log back in")


# logout_and_break(69)
check_login_state_and_login()