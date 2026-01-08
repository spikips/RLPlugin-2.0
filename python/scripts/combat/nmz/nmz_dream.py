from modules.core.plugin_client import npc
from modules.utils.select_menu_option import select_menu_option
from modules.utils.wait_for_tick import wait_for_tick
from modules.widgets.widget import check_widget

def enter_dream():
    """
    Interact with Dominic Onion NPC to select 'Dream' option and check for widget 14352385.
    - Helps in understanding: Retries interaction with timeouts to handle game latency.
    - Bigger picture: Ensures reliable entry into NMZ dream by verifying UI feedback.
    """
    max_attempts = 3
    for attempt in range(1, max_attempts + 1):
        print(f"Attempt {attempt} to enter NMZ dream...")
        
        # Get NPC data
        npc_data = npc()['data']
        
        # Find Dominic Onion
        dominic = next((npc for npc in npc_data if npc.get('name') == 'Dominic Onion'), None)
        if not dominic:
            print("Dominic Onion NPC not found.")
            continue
        
        # Get coordinates
        middle_point = dominic.get('middle_point', {})
        x = middle_point.get('x', 0)
        y = middle_point.get('y', 0)
        if x == 0 and y == 0:
            print("Invalid coordinates for Dominic Onion.")
            continue
        
        # Interact with 'Dream' option
        success = select_menu_option(x, y, "Dream")
        if not success:
            print("Failed to select 'Dream' option on Dominic Onion.")
            continue
        
        # Wait up to 6 ticks for widget 14352385
        max_ticks = 6
        tick_count = 0
        while tick_count < max_ticks:
            if check_widget('14352385'):
                print(f"Widget 14352385 appeared after {tick_count} ticks.")
                return True
            elif check_widget('15138822'):
                print("Widget 15138822 appeared, indicating an existing dream.")
                return True
            wait_for_tick(1)
            tick_count += 1
        
        print(f"Widget 14352385 did not appear after {max_ticks} ticks.")
    
    print("Failed to enter NMZ dream after maximum attempts.")
    return False

if __name__ == "__main__":
    print(enter_dream())