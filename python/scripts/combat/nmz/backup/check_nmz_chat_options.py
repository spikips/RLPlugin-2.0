from modules.widgets.widget import check_widget_text, check_widget
from modules.utils.wait_for_tick import wait_for_tick
import keyboard
import time
import random

def check_nmz_chat_options():
    """Handle NMZ chat options by checking widget text and pressing keys accordingly."""
    # Loop over child indexes 1-6 to find 'rumble'
    rumble_found = False
    for child_index in range(1, 7):
        text = check_widget_text('14352385', child_index=child_index)
        if text and 'rumble' in text.lower():
            print(f"Found 'rumble' at child index {child_index}, pressing '3'...")
            keyboard.press_and_release('3')
            wait_for_tick(2)
            rumble_found = True
            break
    
    if not rumble_found:
        print("No 'rumble' option found in widget 14352385 children 1-6.")
        return False
    
    # After pressing '3', check for 'normal' in children 1-6
    normal_found = False
    for child_index in range(1, 7):
        text = check_widget_text('14352385', child_index=child_index)
        if text and 'customisable - normal' in text.lower():
            print(f"Found 'customisable - normal' at child index {child_index}, pressing '3'...")
            keyboard.press_and_release('3')
            wait_for_tick(2)
            normal_found = True
            break
    
    if not normal_found:
        print("No 'normal' option found after selecting 'rumble'.")
        return False
    
    # Check for widget 15138821
    if check_widget('15138821'):
        print("Widget 15138821 found, proceeding to press space...")
        presses = random.randint(3, 5)
        print(f"Will press space {presses} times")
        for i in range(presses):
            keyboard.press_and_release('space')
            print(f"Pressed space {i+1}/{presses}")
            time.sleep(random.uniform(0.07, 0.15))  # Interval between presses
        
        wait_for_tick(2)
        
        # After pressing space, loop for 'yes' in children 1-6
        yes_found = False
        for child_index in range(1, 7):
            text = check_widget_text('14352385', child_index=child_index)
            if text and 'yes' in text.lower():
                print(f"Found 'yes' at child index {child_index}, pressing '1'...")
                keyboard.press_and_release('1')
                wait_for_tick(2)
                yes_found = True
                break
        
        if not yes_found:
            print("No 'yes' option found after pressing space.")
            return False
        
        return True
    else:
        print("Widget 15138821 not found.")
        return False

if __name__ == "__main__":
    # time.sleep(2)
    print(check_nmz_chat_options())


# nmz 12276, 8536
# walk to 12272, 8551, plane 3