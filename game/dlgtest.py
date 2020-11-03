# %%

from game.core import Graph
from game.dlg import Dialogue, DlgText, DlgGroup, DlgBranch

# %%


TEXTS = [
    {'speaker': 'NPC',
     'text': 'Hello.'},
    {'speaker': 'Player',
     'text': 'Hi!'},
    {'speaker': 'Player',
     'text': 'How r u?'},
    {'speaker': 'NPC',
     'text': 'Great!',
     'condition': {'op': 'ne', 'path': '/world/day', 'value': 'Monday'}},
    {'speaker': 'NPC',
     'text': 'Not great.'},
    {'speaker': 'Player',
     'text': 'Well, that is too bad.',
     'condition': {'op': 'ge', 'path': '/player/stat1', 'value': 6}},
    {'speaker': 'Player',
     'text': 'You deserve it fuckwad!'},
    {'speaker': 'Player',
     'text': "Let's try again."}
]

GAMESTATE = {
    'player': {
        'stat1': 5
    },
    'world': {
        'day': 'Monday'
    }
}

LNS = [DlgText(**txt) for txt in TEXTS]
B1 = DlgBranch()
B2 = DlgBranch()
GRP1 = DlgGroup()
GRP2 = DlgGroup()
G = Graph(edges=[
    (LNS[0], GRP1),
    (GRP1, LNS[1], 'Say hi'),
    (GRP1, LNS[2], 'Ask how are you'),
    (LNS[2], B1, '[Continue]'),
    (B1, LNS[3], 'Dummy text'),
    (B1, LNS[4]),
    (LNS[3], GRP1, 'Dummy text'),
    (LNS[4], B2, '[Continue]'),
    (B2, LNS[5]),
    (B2, LNS[6]),
    (LNS[5], GRP2),
    (LNS[6], GRP2),
    (GRP2, LNS[7], 'Ask to try again.'),
    (LNS[7], GRP1),
])
# %%
dlg = Dialogue(G, GAMESTATE)
dlg.subscribe(dlg.viewListener(print))

# %%
