# %%
# Needed for interactive window relative import
from functools import singledispatch
import sys
from pathlib import Path
from typing import Dict, Optional
import rx.operators as ops
from rx.subject import Subject

sys.path.append(str(Path(__file__).parent.parent))  # nopep8
from game.lib import Graph, StateMachine
from game.dlg import DlgText, DlgGroup, DlgEnd, DlgBranch, DlgNode

# %%


# %%


# %%


def play(dlg):

    while dlg.node:
        if not isinstance(dlg.node, DlgText):
            continue

        print(f'{dlg.node.speaker}: {dlg.node.text}')
        prompt = '[Press any key to continue]'
        if len(dlg.responses) > 1:
            for i, txt in enumerate(dlg.responses):
                print(f'{i+1}. {txt}')

            prompt = 'Select a response: '

        response = input(prompt)
        try:
            dlg.select(int(response) - 1)
        except ValueError:
            dlg.select()

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
     'conditions': [False]},
    {'speaker': 'NPC',
     'text': 'Not great.',
     'conditions': [True]},
    {'speaker': 'Player',
     'text': 'Well, that is too bad.',
     'conditions': [True]},
    {'speaker': 'Player',
     'text': 'You deserve it fuckwad!',
     'conditions': [True]},
]

LNS = [DlgText(**txt) for txt in TEXTS]
B1 = DlgBranch()
GRP1 = DlgGroup()
GRP2 = DlgGroup()
G = Graph(edges=[(LNS[0], GRP1, 'Group edge BAD'),
                 (GRP1, LNS[1], 'Say hi'),
                 (GRP1, LNS[2], 'Ask how are you'),
                 (GRP1, GRP2),
                 (GRP2, LNS[3]),
                 (GRP2, LNS[5], 'Line 5')])

# %%


def getChildren(node: DlgNode, graph: Graph):
    child_data = list()

    for child in graph.get(node, []):
        if all(cond for cond in child.conditions):
            if isinstance(child, DlgGroup):
                child_data += getChildren(child, graph)
            else:
                child_data += [(child, graph[node][child])]

    return child_data


def dlgView(node) -> Optional[Dict]:
    return {'node': node, 'children': getChildren(node, G)} if node else None


@singledispatch
def processNode(node):
    return None


@processNode.register
def processDlgBranch(node: DlgBranch):
    children = tuple(t[0] for t in getChildren(node, G))
    return processNode(children[0]) if children else None


@processNode.register
def processDlgText(node: DlgText):
    return node


def dlgTransition(node, state_input=0):
    children = tuple(t[0] for t in getChildren(node, G))
    state_input = state_input if (state_input or 0) < len(children) else 0
    if children:
        return processNode(children[state_input if state_input < len(children) else 0])

    return None


def dlgOnEnter(node, state_input=0):
    print(f'Input received: {state_input}')
    if isinstance(node, DlgText):
        print(f'{node.speaker}: {node.text}')
        for i, child_data in enumerate(dlgView(node).get('children', [])):
            print(f'{i}. {child_data[1]}')
    else:
        print(f'Current node is {node}')


# %%
sm = StateMachine(list(G)[0], transition=dlgTransition,
                  view=dlgView, onenter=dlgOnEnter)

# %%
