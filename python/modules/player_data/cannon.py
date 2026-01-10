from modules.object_data.game_object import get_closest_game_object
from modules.core.plugin_client import cannon_data, reset_cannon, get_varbits
from modules.core.mouse_control import move
from modules.core.window_utils import runelite_window
from modules.utils.select_menu_option import select_menu_option

def click_cannon(action: str = 'Fire'):  # 'Fire' to reload, 'Pick-up' to pick up, etc.
    """Click your cannon using menu option. Fallback if middle_point missing."""
    data = cannon_data().get('data', {})
    if not data.get('exists'):
        print("No cannon detected")
        return False

    mp = data.get('middle_point')
    if mp is None:
        # Fallback: Query game_object at known position for middle_point
        print("Middle point missing - falling back to game_object query")
        # Parse position string, e.g., 'WorldPoint(x=1423, y=9866, plane=0)'
        pos_str = data.get('position', '')
        if 'WorldPoint' in pos_str:
            parts = pos_str.split('(')[1].split(')')[0].split(',')
            x = int(parts[0].split('=')[1])
            y = int(parts[1].split('=')[1])
            plane = int(parts[2].split('=')[1])
            # Query cannon IDs at exact position (small radius)
            cannon_ids = [6, 7, 8, 9]
            for cid in cannon_ids:
                response = get_closest_game_object(str(cid), (x, y), radius=1)
                if response and 'data' in response and response['data']:
                    obj = response['data'][0]
                    if obj.get('location', {}).get('x') == x and obj.get('location', {}).get('y') == y:
                        mp = obj.get('middle_point')
                        print("Fallback middle_point found:", mp)
                        break

    if mp is None:
        print("Failed to find middle_point even with fallback - rebuild cannon")
        return False

    # Hover and select menu option
    success = select_menu_option(mp['x'], mp['y'], action)
    if success:
        print(f"Successfully performed '{action}' on cannon")
        return True
    else:
        print(f"Failed to '{action}' cannon")
        return False

# Example: Reload cannon
# click_cannon('Fire')

# Test cannon data
# print("Current cannon data:")
# reset_cannon()

# while True:
#    print(cannon_data())

# Optional reset
# print("Cannon data after reset:")
# print(cannon_data())