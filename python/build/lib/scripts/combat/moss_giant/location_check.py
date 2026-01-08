from modules.core.plugin_client import player

def is_inside_polygon(point, polygon):
    """
    Determine if a point is inside a given polygon using ray casting algorithm.
    
    Args:
        point (tuple): (x, y) coordinates of the point.
        polygon (list): List of (x, y) tuples representing the polygon vertices.
    
    Returns:
        bool: True if the point is inside the polygon, False otherwise.
    """
    x, y = point
    n = len(polygon)
    inside = False
    p1x, p1y = polygon[0]
    for i in range(n + 1):
        p2x, p2y = polygon[i % n]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = not inside
        p1x, p1y = p2x, p2y
    return inside

def check_location():
    """
    Check if the player's current location is inside the specified tiles (polygon).
    
    Returns:
        bool: True if inside, False otherwise.
    """
    # Define the polygon vertices (excluding the last repeated point)
    polygon = [
        (2213,3798),
        (2213,3811),
        (2215,3811),
        (2220,3815),
        (2220,3828),
        (2207,3837),
        (2194,3824),
        (2194,3816),
        (2182,3807),
        (2199,3794),
        (2213,3798)
    ]

    # Get player location
    player_data = player(location=True)
    if not player_data or 'data' not in player_data or 'location' not in player_data['data']:
        print("Failed to retrieve player location.")
        return False

    loc = player_data['data']['location']
    player_x = loc['x']
    player_y = loc['y']
    player_z = loc['plane']

    if player_z != 0:
        print(f"Player is on plane {player_z}, expected 0.")
        return False

    point = (player_x, player_y)
    inside = is_inside_polygon(point, polygon)
    if not inside:
        print(f"Player at ({player_x}, {player_y}) is outside the specified area.")
    return inside

# Test the function
# while True:
#     print(check_location())
#     time.sleep(0.6)