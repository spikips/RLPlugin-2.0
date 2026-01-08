from modules.widgets.widget import check_widget_text, check_widget
import keyboard
import time
from modules.utils.wait_for_tick import wait_for_tick
import random
from modules.core.plugin_client import stats
import json
import os
import re

def check_dream_widget(widget_id='15138822'):
    """
    Check if the widget contains 'I've already created a dream for you.' text.
    
    Args:
        widget_id (str): The widget ID to check (default: '15138822').
    
    Returns:
        bool: True if the dream created text is found, False otherwise.
    """
    # Try the parent widget first
    text = check_widget_text(widget_id)
    print(f"Checking widget {widget_id}: {text}")
    if text:
        # Remove HTML-like tags and normalize text for comparison
        clean_text = re.sub(r'<[^>]+>', '', text).lower()
        if "i've already created a dream for you" in clean_text:
            print("Already created a dream, no further action needed.")
            return True
    
    # Check child widgets (indices 1 to 7, as per original loop)
    for child_index in range(1, 7):
        text = check_widget_text(widget_id, child_index=child_index)
        print(f"Checking widget {widget_id} child {child_index}: {text}")
        if text:
            clean_text = re.sub(r'<[^>]+>', '', text).lower()
            if "i've already created a dream for you" in clean_text:
                print("Already created a dream in child widget, no further action needed.")
                return True
    
    print("No dream created text found in widget or its children.")
    return False

def check_nmz_chat_options():
    """Handle NMZ chat options by checking widget text and pressing keys accordingly.
    - Helps in understanding: Dynamically detects and selects options based on player stats (ranged or magic level depending on config style) and widget content.
    - Bigger picture: Automates dream setup for appropriate difficulty and mode, ensuring optimal NMZ session start tailored to the active combat style.
    """
    # Load config for style
    script_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(script_dir, 'config.json')
    try:
        with open(json_path, 'r') as f:
            config = json.load(f)
            style = config.get('style', 'range')
    except FileNotFoundError:
        print(f"{json_path} not found.")
        return False
    except json.JSONDecodeError:
        print("Invalid JSON in config.json.")
        return False

    # Get player's relevant level based on style
    player_stats = stats()['data']
    if style == 'range':
        level = player_stats['Ranged']['level']
        level_type = 'Ranged'
    elif style == 'magic':
        level = player_stats['Magic']['level']
        level_type = 'Magic'
    else:
        print(f"Invalid style: {style}.")
        return False
    print(f"Player's {level_type} level: {level}")

    # Determine difficulty based on relevant level
    if level >= 40:
        difficulty_text = 'customisable - hard'
        difficulty_key = '4'
    else:
        difficulty_text = 'customisable - normal'
        difficulty_key = '3'

    # Loop over child indexes 1-6 to find 'rumble' or 'already created a dream'
    rumble_found = False
    already_dream = False
    start_time = time.time()
    while time.time() - start_time < 2:  # Max 2 seconds
        for child_index in range(1, 7):
            text = check_widget_text('14352385', child_index=child_index)
            if text:
                lower_text = text.lower()
                if 'rumble' in lower_text:
                    print(f"Found 'rumble' at child index {child_index}, pressing '3'...")
                    keyboard.press_and_release('3')
                    rumble_found = True
                    break
        
        if not rumble_found:
            # Integrated dream check for efficiency (single call instead of loop)
            if check_dream_widget('15138822'):
                already_dream = True

        if rumble_found or already_dream:
            break
        time.sleep(0.05)  # Check every 0.05 seconds
    
    if already_dream:
        return True
    
    if not rumble_found:
        print("No 'rumble' option found in widget 14352385 children 1-6.")
        return False
    
    # After pressing '3', check for the selected difficulty in children 1-6
    difficulty_found = False
    start_time = time.time()
    while time.time() - start_time < 2:  # Max 2 seconds
        for child_index in range(1, 7):
            text = check_widget_text('14352385', child_index=child_index)
            if text and difficulty_text in text.lower():
                print(f"Found '{difficulty_text}' at child_index {child_index}, pressing '{difficulty_key}'...")
                keyboard.press_and_release(difficulty_key)
                difficulty_found = True
                break
        if difficulty_found:
            break
        time.sleep(0.05)  # Check every 0.05 seconds
    
    if not difficulty_found:
        print(f"No '{difficulty_text}' option found after selecting 'rumble'.")
        return False
    
    widget_found = False
    # Check for widget 15138821
    start_time = time.time()
    while time.time() - start_time < 2:  # Max 2 seconds
        if check_widget('15138821'):
            print("Widget 15138821 found, proceeding to press space...")
            presses = random.randint(3, 5)
            print(f"Will press space {presses} times")
            for i in range(presses):
                keyboard.press_and_release('space')
                print(f"Pressed space {i+1}/{presses}")
                time.sleep(random.uniform(0.07, 0.15))  # Interval between presses
                widget_found = True
            break
        time.sleep(0.05)  # Check every 0.05 seconds
    
    if not widget_found:
        print("Widget 15138821 not found.")
        return False
    
    # After pressing space, loop for 'yes' in children 1-6
    yes_found = False
    start_time = time.time()
    while time.time() - start_time < 2:  # Max 2 seconds
        for child_index in range(1, 7):
            text = check_widget_text('14352385', child_index=child_index)
            if text and 'yes' in text.lower():
                print(f"Found 'yes' at child_index {child_index}, pressing '1'...")
                keyboard.press_and_release('1')
                yes_found = True
                wait_for_tick(1)
                break
        if yes_found:
            break
        time.sleep(0.05)  # Check every 0.05 seconds
    
    if not yes_found:
        print("No 'yes' option found after pressing space.")
        return False
    
    return True


if __name__ == "__main__":
    # time.sleep(2)
    print(check_nmz_chat_options())


# nmz 12276, 8536
# walk to 12272, 8551, plane 3