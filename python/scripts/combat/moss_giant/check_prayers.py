from modules.core.plugin_client import get_active_prayers

def check_active_prayers():
    """
    Check which prayers are currently active using the plugin client's get_active_prayers method.
    Prints only active prayers or "no prayers active" if none are enabled.

    Returns:
        dict: Mapping of active prayer names to boolean (True).
    """
    prayer_data = get_active_prayers()
    if not prayer_data:
        print("Failed to retrieve prayer data.")
        return {}

    # Access the 'data' key where the prayer statuses are stored
    prayers = prayer_data.get('data', {})
    if not prayers:
        print("No prayer data available.")
        return {}

    # Filter for active prayers (value = True)
    active_prayers = {prayer: status for prayer, status in prayers.items() if status}

    if not active_prayers:
        print("no prayers active")
    else:
        print("Active prayers:", {k: v for k, v in active_prayers.items()})

    return active_prayers

# while True:
#     time.sleep(0.6)
#     check_active_prayers()