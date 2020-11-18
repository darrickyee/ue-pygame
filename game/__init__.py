# %%
from typing import Any, Container, Mapping
import rx.operators as ops
from game.lib import evaluator, on_change
from game.core import World, EcsStore, EcsGameSystem
from game.core.systems import InventorySystem, LocationSystem
from game.dlgtest import G
from game.dlg import Dialogue
# %%


def pick(props: Container[str], obj: Mapping[str, Any]):
    return {prop: obj[prop] for prop in obj if prop in props}


# class TargetSystem(EcsGameSystem):

#     @property
#     def actions(self):
#         return {'PLAYER_TARGET': self._update_target}

#     def _update_target(self, data: dict):
#         world = self.store.get_component('game', 'world')
#         world['target'] = {
#             'name': self.store.get_component(data['entity'], 'displayname') or '',
#             'color': [1, 0.2, 0.2],
#             'interact': None
#         }

#         self.store.set_component('game', 'world', world)


# # %%

# WORLD = {
#     'game': {
#         'datetime': {
#             'daynumber': 1,
#             'day': 'Monday',
#             'time': 'Morning'
#         },
#         'dialogue': {
#             'speaker': '',
#             'text': '',
#             'responses': []
#         },
#         'target': None
#     }
# }

# LOCATION = {
#     'player': {
#         'level': None,
#         'area': None
#     },
#     'npc1': {
#         'level': 'Home',
#         'area': None
#     },
#     'npc2': {
#         'level': 'Store',
#         'area': None
#     }
# }

# DISPLAYNAME = {
#     'player': 'Player',
#     'npc1': 'Bob',
#     'npc2': 'Karen',
#     'gold': 'Gold',
#     'shoe': 'Old shoe'
# }

# CHARBASE = {
#     'player': {'female': False},
#     'npc1': {'female': False},
#     'npc2': {'female': True}
# }

# ITEMBASE = {
#     'gold': {'name': 'Gold', 'maxcount': -1},
#     'shoe': {'name': 'Old shoe', 'maxcount': 1}
# }

# INVENTORY = {
#     'player': {'gold': 299}
# }

# EQUIPPABLE = {
#     'shoe': {'slot': 'feet'}
# }

# INITSTATE = {
#     'world': WORLD,
#     'location': LOCATION,
#     'itembase': ITEMBASE,
#     'inventory': INVENTORY,
#     'equippable': EQUIPPABLE,
#     'displayname': DISPLAYNAME,
#     'charbase': CHARBASE
# }


# GAME = World(EcsStore(INITSTATE))
# GAME.add_system(LocationSystem)
# GAME.add_system(TargetSystem)
# GAME.add_system(DialogueSystem)
# GAME.add_system(InventorySystem)


# """
#     - Player changes location
#     - Player advances time
#     - Player interacts with object
#     - Player selects option/response

# Need computed values
#     """

# # %%


# stream1 = GAME.events.pipe(
#     on_change('/location/player/level'),
#     ops.filter(evaluator({'path': '/location/player/level', 'op': 'eq', 'value': 'ThirdPersonExampleMap'})
#                )
# )

# dlgstream = GAME.events.pipe()
# dlgstream.subscribe(print)


# def launchDlg(event: dict):
#     # ue.log('Launching dialogue...')
#     # for d in disp:
#     #     d.dispose()
#     print('Launching dialogue...')
#     GAME.dispatch({'action_type': 'START_DIALOGUE'})
#     GAME.dispatch({'action_type': 'PLAYER_MOVE',
#                    'data': {'level': 'Somewhere else'}})


# stream1.subscribe(launchDlg)
# GAME.events.subscribe(print)
# GAME._actions.subscribe(lambda a: print(f'Action: {a}'))
# # %%
