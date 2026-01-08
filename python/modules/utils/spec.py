from modules.widgets.widget import check_widget_text, check_widget, click_widget
from modules.utils.wait_for_tick import wait_for_tick


def spec(threshold=50):
    spec_level_str = check_widget_text('10485796')
    try:
        spec_level = int(spec_level_str)
    except ValueError:
        exit('Invalid spec level text')

    if spec_level >= threshold:
        if not check_widget('10485797', sprite_id=1608):
            click_widget('10485797')
            # wait_for_tick(1)  # Wait for game to register click
        return True  # Indicate successful spec or no action needed
    return False  # Indicate insufficient energy


# while True:
#     if spec():  # Only continue if spec was successful or not needed
#         wait_for_tick(1)  # Adjust wait time based on game tick rate or energy regen