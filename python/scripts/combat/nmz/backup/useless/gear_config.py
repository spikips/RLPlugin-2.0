# Centralized configuration for gear sets and item properties

# Gear sets for different Ranged level ranges
GEAR_SETS = {
    (40, 49): [
        'Dorgeshuun crossbow',
        'Holy sandals',
        "Green d'hide chaps",
        'Bone bolts',
        "Green d'hide shield",
        "Green d'hide vambraces",
        'Ancient cloak',
        'Warrior ring',
        "Green d'hide body",
        'Amulet of fury',
        'Saradomin mitre'
    ],
    (50, 59): [
        'Dorgeshuun crossbow',
        'snakeskin boots',
        "blue d'hide chaps",
        'Bone bolts',
        "blue d'hide shield",
        "blue d'hide vambraces",
        'Ancient cloak',
        'Warrior ring',
        "blue d'hide body",
        'Amulet of fury',
        'archer helm'
    ],
    (60, 69): [
        'Dorgeshuun crossbow',
        'snakeskin boots',
        "red d'hide chaps",
        'Bone bolts',
        "red d'hide shield",
        "red d'hide vambraces",
        'mixed hide cape',
        'Warrior ring',
        "red d'hide body",
        'Amulet of fury',
        'archer helm'
    ],
    (70, 99): [
        'magic shortbow (i)',
        'snakeskin boots',
        "black d'hide chaps",
        'Amethyst arrow',
        "black d'hide vambraces",
        "ava's accumulator",
        'Lightbearer',
        "black d'hide body",
        'Amulet of fury',
        'armadyl coif'
    ]
}

# Items that are withdrawn with quantity='all' (e.g., ammo)
AMMO_ITEMS = [
    'Bone bolts',
    'Broad bolts',
    'Diamond bolts (e)',
    'Amethyst arrow'
]