# %%
# Needed for interactive window relative import
from functools import singledispatch, singledispatchmethod
from game.lib import predicate
from typing import Any, Dict
import rx.operators as ops
from rx.subject import Subject

from game.lib import Graph, StateMachine, bind_data
from game.dlg import DlgText, DlgGroup, DlgEnd, DlgBranch, DlgNode


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
     'conditions': [{'op': 'ne', 'path': '/world/day', 'value': 'Monday'}]},
    {'speaker': 'NPC',
     'text': 'Not great.'},
    {'speaker': 'Player',
     'text': 'Well, that is too bad.',
     'conditions': [{'op': 'ge', 'path': '/player/stat1', 'value': 5}]},
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

class DlgPlayer:

    def __init__(self, graph: Graph, context: Any = None) -> None:
        self._graph = graph
        self._context = context or {}

    @property
    def condition(self):
        if self._context:
            return predicate.bind_data(self._context)

        return lambda _: True

    def _childdata(self, node: DlgNode):
        child_data = list()
        for child in self._graph.get(node, []):
            if not child.conditions or all(self.condition(cond)
                                           for cond in child.conditions):
                if isinstance(child, DlgGroup):
                    child_data += self._childdata(child)
                else:
                    child_data += [(child, self._graph[node][child])]

        return child_data

    def view(self, node: DlgNode) -> Dict[str, Any]:
        nodes, responses = tuple(), tuple()

        if (child_data := self._childdata(node)):
            nodes, responses = tuple(zip(*child_data))

        return {'node': node,
                'children': nodes,
                'responses': responses,
                'context': self._context} if node else {}

    def transition(self, node: DlgNode, fsm_input=None):
        fsm_input = fsm_input or 0
        if children := self.view(node).get('children', []):
            return children[fsm_input if fsm_input < len(children) else 0]

        return None

    def action(self, event: dict[str, Any]) -> None:
        if event.get('event_type', None) == 'ENTER':
            return self._action(event.get('state', None), event)

    @singledispatchmethod
    def _action(self, node, event):
        print('Dialogue ended.')

    @_action.register
    def _action_DlgText(self, node: DlgText, event):
        print(f'{node.speaker}: {node.text}')
        for i, response in enumerate(self.view(node)['responses']):
            print(f'{i}. {response}')

        sym = input('Enter a response: ')
        try:
            sym = int(sym)
        except ValueError:
            sym = 0

        event['target'].next(sym)

    @_action.register
    def _action_DlgBranch(self, node: DlgBranch, event):
        event['target'].next()


# %%

def playDlg(graph: Graph, context: Any = None):
    player = DlgPlayer(graph, context)
    sm = StateMachine(
        list(graph)[0], transition=player.transition, action=player.action)
    player.action(sm._event('ENTER'))

# %%
