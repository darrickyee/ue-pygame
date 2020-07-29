# %%
import typing as T
import json
import jsonpatch as jsp
import rx.operators as ops
from rx.subject import Subject

# Add/remove items from inventory
# Equip/unequip items
# Set locations according to schedule
# Update target
# Stats/xp addition
# Modifiers to static abilities
# Modifiers to stats/item addition

class Store:
    ls: T.List[float] = None
    dc: T.Dict[str, Subject]

    def __init__(self, init_state=None):
        self._state = init_state or {}
        self._subject = Subject()
        self.subscribe = self._subject.subscribe

    def getState(self):
        return json.loads(json.dumps(self._state))

    def apply_patch(self, patch: list):
        newstate = jsp.apply_patch(self._state, patch)
        diff = jsp.make_patch(self._state, newstate)
        if diff:
            for patch in diff:
                self._subject.on_next(patch)
            self._state = newstate
# %%
# Components


EVENTS = Subject()
itemevents = EVENTS.pipe(ops.filter(
    lambda e: e.get('etype', None) == 'addItem'))

DISPLAYNAME = {
    'it_gold': 'Gold',
    'player': 'MC',
    'bill': 'Bill',
    'it_sword': 'Bigass Sword'
}

ITEMPROP = {
    'it_gold': {'stacksize': -1,
                'maxcount': -1},
    'it_potion': {
        'stacksize': 99,
        'maxcount': -1
    },
    'it_sword': {
        'stacksize': 1,
        'maxcount': 1,
        'equippable': True,
        'equipslot': 'rHand'
    }
}


INVENTORY = {
    'player': {'it_gold': 230,
               'it_sword': 1},
    'bill': {'it_gold': 890}
}


COMPONENTS = {
    'itemprop': ITEMPROP,
    'displayname': DISPLAYNAME,
    'inventory': INVENTORY
}


def entity(name):
    return {k: v[name] for k, v in COMPONENTS.items() if name in v}


debugdisp = EVENTS.subscribe(print)


def dispatch(event):
    EVENTS.on_next(event)


def itemEventHandler(event):
    actor = event['data']['actor']
    item = event['data']['item']
    count = event['data']['count']
    inv = entity(actor).get('inventory', None)
    if inv:
        inv[item] = inv.get(item, 0) + count

# %%


st = Store({'displayName': {'player': {'name': 'MC', 'color': [0.15, 0.15, 1]},
                            'bob': {'name': 'Bob', 'color': [0, 1, 0]}}})
st.subscribe(print)
# %%
