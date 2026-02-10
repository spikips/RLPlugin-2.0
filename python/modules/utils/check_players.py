# Add this to your utils/detection file (e.g., player_detection.py or in plugin_client.py)

from modules.core.plugin_client import players
from modules.utils.check_if_in_area import point_in_polygon
from typing import List, Tuple

from modules.utils.wait_for_tick import wait_for_next_tick

def check_for_players(ticks: int = 1, radius: int = 50, max_wait_ticks: int = 120) -> bool:
    """
    Check if any player is visible for at least `ticks` consecutive game ticks.
    
    Args:
        ticks (int): Number of consecutive ticks a player must be detected (default: 1).
        radius (int): Radius for players() query (default: 50).
        max_wait_ticks (int): Maximum ticks to wait before giving up (prevents infinite loop).
    
    Returns:
        bool: True if any player was detected for `ticks` consecutive ticks, False otherwise.
    """
    consecutive_detections = 0
    
    for _ in range(max_wait_ticks):
        wait_for_next_tick()  # Sync to game tick
        
        data = players(radius=radius)
        has_players = data is not None and data.get('data') and len(data['data']) > 0
        
        if has_players:
            consecutive_detections += 1
            print(f"Player(s) detected ({consecutive_detections}/{ticks} consecutive ticks)")
            if consecutive_detections >= ticks:
                print(f"Player lingered for {ticks} consecutive ticks - returning True")
                return True
        else:
            if consecutive_detections > 0:
                print(f"Players disappeared - resetting counter")
            consecutive_detections = 0
    
    print(f"No player lingered for {ticks} consecutive ticks after {max_wait_ticks} ticks check")
    return False


def check_for_player_in_area(polygon: List[Tuple[int, int]], radius: int = 50) -> bool:
    """
    Check if any player is inside the specified polygon area.
    
    Args:
        polygon (List[Tuple[int, int]]): List of (x, y) tuples defining the polygon (closed automatically).
        radius (int): Radius to query nearby players (default: 50 - covers most spots safely).
    
    Returns:
        bool: True if at least one player is inside the polygon, False otherwise.
    """
    data = players(radius=radius)
    if not data or not data.get('data'):
        return False
    
    for player_data in data['data']:
        loc_str = player_data.get('location', '')
        if not loc_str:
            continue
        
        # Parse WorldPoint string: "WorldPoint(x=3495, y=3315, plane=0)"
        try:
            x_part = loc_str.split('x=')[1].split(',')[0]
            y_part = loc_str.split('y=')[1].split(',')[0]
            px = int(x_part)
            py = int(y_part)
            
            if point_in_polygon(polygon, px, py):
                print(f"Player '{player_data.get('name', 'Unknown')}' detected inside area at ({px}, {py})")
                return True
        except (IndexError, ValueError):
            print(f"Failed to parse location for player: {loc_str}")
            continue
    
    return False

# === Usage Example ===
# AREA_POLYGON = [
#     (3494, 3322),
#     (3496, 3323),
#     (3497, 3323),
#     (3499, 3322),
#     (3502, 3322),
#     (3503, 3323),
#     (3508, 3323),
#     (3512, 3323),
#     (3518, 3317),
#     (3518, 3314),
#     (3516, 3312),
#     (3512, 3311),
#     (3510, 3309),
#     (3504, 3309),
#     (3498, 3312),
#     (3496, 3312),
#     (3495, 3314),
#     (3494, 3314),
#     (3492, 3316),
#     (3492, 3318),
#     (3491, 3320),
# ]

# if check_for_player_in_area(AREA_POLYGON):
#     print("Player in area - react/hop!")
# else:
#     print("Area clear")

# Quick check (1 tick = instant detection)
# if check_for_players(ticks=1):
#     print("Player spotted!")