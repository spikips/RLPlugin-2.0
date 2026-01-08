from modules.core.mouse_control import move, get_cursor_pos
import time

time.sleep(1)
current_x, current_y = get_cursor_pos()

for _ in range(258):
    move(current_x, current_y, button="left", fast=True, sleep=True)
    move(current_x + 40, current_y, button="left", fast=True, sleep=True)