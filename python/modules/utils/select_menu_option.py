from modules.core.window_utils import runelite_window
from modules.core.plugin_client import interact_options
from modules.core.mouse_control import move, left_click
import time
import random
from typing import Optional, Dict, Any
import re


def select_menu_option(x: int, y: int, action: str, hover_only: bool = False, fast: bool = False) -> Optional[Dict[str, Any]]:
    """
    Hovers over a given location, checks for an action in the context menu, and optionally clicks.
    Matches both exact 'option' or combined 'option' and 'target' (e.g., 'Climb' or 'Climb ladder').
    Clicks a random point within a small range around the option's middle point.
    
    Args:
        x (int): X-coordinate relative to the window
        y (int): Y-coordinate relative to the window
        action (str): The desired action to select (e.g., 'Climb', 'Climb ladder')
        hover_only (bool): If True, only hovers over the action without clicking (default: False)
    
    Returns:
        Optional[Dict[str, Any]]: The selected option data if successful, None otherwise
    """
    # Calculate screen coordinates using runelite_window
    rl_x, rl_y = runelite_window(0, 0)
    screen_x = rl_x + x
    screen_y = rl_y + y
    
    # Hover to load interaction options
    move(screen_x, screen_y, fast=fast, sleep=fast)
    time.sleep(random.uniform(0.03, 0.05))
    
    # Get available interaction options
    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available.")
        return None
    
    # Normalize action for comparison
    action_normalized = ' '.join(action.lower().split())
    
    def clean_target(target: str) -> str:
        return re.sub(r'<[^>]+>', '', target).strip().lower()
    
    # Check if the first option matches the desired action
    first_option = options[0]
    first_option_target_clean = clean_target(first_option['target'])
    first_option_combined = f"{first_option['option'].lower()} {first_option_target_clean}".strip()
    print(f"Checking first option: option='{first_option['option']}', target='{first_option['target']}', combined='{first_option_combined}'")
    
    if first_option['option'].lower() == action_normalized or first_option_combined == action_normalized:
        print(f"Matched first option: {first_option}")
        if not hover_only:
            click_x = screen_x
            click_y = screen_y
            move(click_x, click_y, fast=fast, sleep=fast)
            time.sleep(random.uniform(0.03, 0.05))
            left_click()
        return first_option
    
    # If not top option, right-click to open full context menu and refresh options
    print("Top option mismatch -> right-clicking to open full context menu...")
    move(screen_x, screen_y, fast=fast, sleep=fast, button='right')
    time.sleep(random.uniform(0.03, 0.05))
    
    # Refresh options now that menu is open
    options = interact_options().get('data', [])
    if not options:
        print("No interaction options available after right-click.")
        return None
    
    # Look for the action in the refreshed context menu
    matched_option = None
    for option in options:
        option_target_clean = clean_target(option['target'])
        option_combined = f"{option['option'].lower()} {option_target_clean}".strip()
        print(f"Checking option: option='{option['option']}', target='{option['target']}', combined='{option_combined}'")
        
        if option['option'].lower() == action_normalized or option_combined == action_normalized:
            matched_option = option
            break
    
    if not matched_option:
        clean_opts = [f"{opt['option']} {clean_target(opt['target'])}" for opt in options]
        print(f"No '{action}' option found. Available options: {clean_opts}")
        move(screen_x + random.randint(-6, 6), screen_y + random.randint(50, 120), fast=fast, sleep=fast)
        return None
    
    print(f"Matched context menu option: {matched_option}")
    
    if hover_only:
        return matched_option
    
    # Click the exact middle point with small horizontal randomness only
    mid = matched_option['middle_point']
    click_x = rl_x + mid['x'] + random.randint(-6, 6)
    click_y = rl_y + mid['y']  # Exact vertical (no offset to avoid crossing 15px boundaries)
    
    move(click_x, click_y, fast=fast, sleep=fast)
    time.sleep(random.uniform(0.03, 0.05))
    left_click()
    
    return matched_option

# select_menu_option(249, 140, "Take absorption potion")
