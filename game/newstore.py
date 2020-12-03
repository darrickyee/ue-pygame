from game.lib import ObsList, ObsDict

LOCATION = {
    'player': {
        'level': None,
        'area': None
    },
    'npc1': {
        'level': 'Home',
        'area': None
    },
    'npc2': {
        'level': 'Store',
        'area': None
    }
}

DISPLAYNAME = {
    'player': 'Player',
    'npc1': 'Bob',
    'npc2': 'Karen',
    'gold': 'Gold',
    'shoe': 'Old shoe'
}

CHARBASE = {
    'player': {'female': False},
    'npc1': {'female': False},
    'npc2': {'female': True}
}

ITEMBASE = {
    'gold': {'name': 'Gold', 'maxcount': -1},
    'shoe': {'name': 'Old shoe', 'maxcount': 1}
}

INVENTORY = {
    'player': {'gold': 299}
}
