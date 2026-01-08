import time
from modules.core.plugin_client import gametick

def wait_for_tick(ticks=1):
    for _ in range(ticks):
        current_tick = gametick().get('data', 0)
        while gametick().get('data', 0) <= current_tick:
            time.sleep(0.01)  # Short sleep to poll frequently
    return True
