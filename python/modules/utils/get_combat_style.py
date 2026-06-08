from modules.core.plugin_client import attack_style, get_attack_style_name, combat_style
import time

# while True:
print("Rich style:", attack_style())
print("Name only:", get_attack_style_name())
print("Old simple style (still works):", combat_style())