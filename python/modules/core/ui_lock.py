import asyncio

# Global asyncio lock used to serialize UI interactions (click_widget, click_inventory, etc.)
# Import and use with: `from modules.core.ui_lock import ui_lock` and `async with ui_lock:`
ui_lock = asyncio.Lock()
