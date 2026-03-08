from leather import craft_leather
from cut_sapphire import cut_sapphires
from modules.player_data.get_level import get_level

def get_crafting_level():
    return get_level("Crafting")

while True:
    crafting_level = get_crafting_level()
    if crafting_level >= 20:
        cut_sapphires(allow_break=False)
    elif crafting_level >= 1:
        print("Crafting level is " + str(crafting_level) + " - starting leather crafting")
        craft_leather()


