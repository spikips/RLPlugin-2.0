from modules.core.plugin_client import game_state
from modules.utils.wait_for_tick import wait_for_tick
from modules.widgets.widget import check_widget_text, click_widget, check_widget, get_widget
from modules.core.mouse_control import move
from modules.widgets.widget_data import get_all_widget_data
from modules.core.window_utils import runelite_window, focus_runelite_window
import keyboard
import time, re, random

_quick_hop = False

def quickhop_widget():
    global _quick_hop
    print(_quick_hop)
    # checks the logout tab
    if not _quick_hop:
        if check_widget('35913779', sprite_id=-1):
            print('opening logout widget')
            # opens the logout tab
            click_widget('35913779', rand_x=10, rand_y=10)
            # opens the hop widget
            click_widget('11927559')
            while not check_widget('4522004'):
                time.sleep(0.1)
            _quick_hop = True
            return True
        elif check_widget('11927559'):
            click_widget('11927559')
            _quick_hop = True
            return True
    return False

def logout_widget():
    if check_widget('35913779', sprite_id=-1):
        keyboard.press('f5')
        time.sleep(random.uniform(0.039, 0.081))
        keyboard.release('f5')
        # opens the hop widget
        if click_widget('11927559'):
            while not check_widget('4522004'):
                time.sleep(0.1)

def extract_world_number(text):
    if text is None:
        return None
    match = re.search(r'\d+$', text)
    if match:
        return int(match.group())
    return None

def get_hop_worlds(membership='p2p'):
    current_world_text = check_widget_text("4521987")
    print(current_world_text, "current world")
    current_world = extract_world_number(current_world_text)
    min_y = 242
    max_y = 432
    color = 15790080 if membership == 'p2p' else 14737632
    sprite_id = 1131 if membership == 'p2p' else 1130
    widgets = get_all_widget_data()
    try:
        parent = next(w for w in widgets if w['id'] == 4522003)
    except StopIteration:
        return None
    children = parent['children']
    results = []
    index = 2
    while index < len(children):
        name_child = children[index]
        sprite_index = index - 1
        text_index = index + 3
        if sprite_index < 0 or sprite_index >= len(children) or text_index >= len(children):
            index += 6
            continue
        sprite_child = children[sprite_index]
        text_child = children[text_index]
        if name_child['textColor'] == color and sprite_child['spriteId'] == sprite_id:
            text_lower = text_child['text'].lower()
            # Exclude if text contains "pvp" or "high risk"
            if "pvp" in text_lower or "high risk" in text_lower or "grid master" in text_lower or "bounty" in text_lower:
                index += 6
                continue
            # Extract world number from name text
            world_num = int(name_child['text']) if name_child['text'].isdigit() else None
            if world_num != current_world and min_y <= name_child['random_clickpoint']['y'] <= max_y:
                results.append({
                    'random_clickpoint': name_child['random_clickpoint'],
                    'name': name_child['name'],
                    'text': text_child['text'],
                    'world': name_child['text']
                })
        index += 6
    if results:
        chosen = random.choice(results)
        screen_x, screen_y = runelite_window(chosen['random_clickpoint']['x'], chosen['random_clickpoint']['y'])
        chosen['screen_x'] = screen_x
        chosen['screen_y'] = screen_y
        print(f"Chosen world: {chosen['world']} at screen ({screen_x}, {screen_y})")
        return chosen
    return None

def hop_to_random_world(membership='p2p'):
    if not _quick_hop:
        quickhop_widget()
        while not check_widget('4522004'):
            time.sleep(0.05)
    else:
        # opens the logout tab
        click_widget('35913779', rand_x=10, rand_y=10)
        while not get_hop_worlds(membership):
            time.sleep(0.01)
    
    max_scroll_attempts = 10
    scroll_attempts = 0
    world = get_hop_worlds(membership)

    while not world and scroll_attempts < max_scroll_attempts:
        print(f"No worlds found, attempting to scroll (attempt {scroll_attempts + 1}/{max_scroll_attempts})")
        if click_scrollbar(membership):
            time.sleep(0.05)  # Brief pause to allow the scroll to take effect
            world = get_hop_worlds(membership)
        else:
            print("Failed to click scrollbar")
            time.sleep(0.1)
        scroll_attempts += 1
    
    if not world:
        print("world list not found after scrolling attempts: ", world)
        exit()
    
    screen_x = world['screen_x']
    screen_y = world['screen_y']
    print(f"Hopping to world: {world['world']}")
    focus_runelite_window()
    move(screen_x, screen_y, button='left', fast=True, sleep=True)
    wait_for_tick(3)
    while True:
        state = game_state()
        if state['data'] == 'LOGGED_IN':
            time.sleep(0.1)
            click_scrollbar(membership)
            break

def click_scrollbar(membership='p2p', parent_id='4522004', max_attempts=10):
    """
    Loops clicking random safe points in the scrollbar until a valid world is found.
    
    :param membership: Membership type for get_hop_worlds.
    :param parent_id: The ID of the parent widget.
    :param max_attempts: Maximum scroll click attempts before giving up.
    """
    # Get the child1 widget to determine the forbidden y area
    child1 = get_widget(parent_id, child_index=1)
    forbidden_y = child1['bounds']['y']  # Top y of the small widget (e.g., button)
    lower_tolerance = 1
    upper_tolerance = 11
    
    attempts = 0
    while attempts < max_attempts:    
        # Get a random point in the large child0 area (canvas coordinates)
        child0 = get_widget(parent_id, child_index=0)
        canvas_x = child0['random_clickpoint']['x']
        canvas_y = child0['random_clickpoint']['y']
        # Check if the canvas_y is outside the forbidden zone
        if not (forbidden_y - lower_tolerance <= canvas_y <= forbidden_y + upper_tolerance):
            # Safe to click: convert to screen and click
            click_x, click_y = runelite_window(canvas_x, canvas_y)
            move(x=click_x, y=click_y, button='left', fast=True, sleep=True)
            print(f"Safe scroll click performed at canvas ({canvas_x}, {canvas_y}) -> screen ({click_x}, {click_y})")
            
            # Brief wait for scroll effect, then check for world
            time.sleep(0.02)
            if get_hop_worlds(membership):
                print("World found after scroll click.")
                return True
        
        attempts += 1
        # Quick delay before next attempt
        time.sleep(0.02)

        # Check if a world is already available (quick check before clicking)
        if not get_hop_worlds(membership):
            print("no world found, attempting scroll click")
        else:
            print("World found without needing to scroll.")
            return True
    
    print(f"Failed to find a world after {max_attempts} scroll attempts. Forbidden y: {forbidden_y} ± ({lower_tolerance}, {upper_tolerance})")
    return False

# print(runelite_window(0, 0))
# hop_to_random_world()
# quickhop_widget()
# click_scrollbar()
# print(get_hop_worlds())