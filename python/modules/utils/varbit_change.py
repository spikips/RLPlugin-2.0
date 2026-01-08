from modules.core.plugin_client import varbit_changes
import time

while True:
    changes = varbit_changes()
    # print(changes)
    if changes and 'data' in changes:
        for change in changes['data']:
            print(f"Varbit {change['varbit']} changed: {change['old']} -> {change['new']} (tick {change['tick']})")
    print('-\n')
    time.sleep(0.6)  # Tick sync