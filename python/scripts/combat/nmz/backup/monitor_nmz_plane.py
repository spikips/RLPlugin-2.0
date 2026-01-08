from modules.core.plugin_client import player
from modules.utils.wait_for_tick import wait_for_tick
from handle_prayer import check_prayer_points
import random

def monitor_nmz_plane():
    """Loop checking if plane == 3 (inside NMZ), continue until plane == 0."""
    drink_threshold = random.randint(1, 27)
    while True:
        data = player(location=True)
        if data and 'data' in data and 'location' in data['data']:
            plane = data['data']['location']['plane']
            print(f"Current plane: {plane}")
            if plane == 0:
                print("Exited NMZ (plane == 0).")
                return True
        else:
            print("Failed to get location.")
        check_prayer_points(drink_threshold=drink_threshold)
        wait_for_tick(1)  # Check every tick

if __name__ == "__main__":
    monitor_nmz_plane()