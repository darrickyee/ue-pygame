import os
import json
import ue_pylink
from .db import loadDB
from .dlg import loadDlgGraphs, DlgGraph
from .ecs import handler, System, EntityManager

DB_PATH = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)))


# GLOBALS: Fixed data e.g. dlgs, quests, locations
# All else in components
# MODDB: Initialize components?


def omit(keys, d):
    return {k: v for k, v in d.items() if k not in keys}


def loadComponents(tables, keys=None):
    keys = keys or tuple(tables.keys())
    ctables = {k: t for k, t in tables.items() if k in keys}
    return {k: {row.get('id', None): omit(['id'], row) for row in t} for k, t in ctables.items()}


COMPDB = loadDB(os.path.realpath(DB_PATH + '/game.db'))
for ctype in 'dlg_reader', 'interact', 'dlg':
    COMPDB[ctype] = []

EM = EntityManager(loadComponents(COMPDB))

EM.addComponent('player', {'type': 'dlg_reader'})

for npc in (eid for eid in EM.entity_ids if eid != 'player'):
    EM.addComponent(
        npc, {'type': 'interact', 'action1': {'type': 'DLG_START', 'name': 'Talk'}})


GAMEDB = loadDlgGraphs()


# %%


def SendEvent(name: str, data: str = None):
    ue_pylink.broadcast(name, data)  # pylint: disable=no-member
    # print(f'{name}: {data}')


DLGSYSTEM = System()
NODEDATA = {'speaker': '',
            'text': '',
            'responses': []}


def getNodeData(*args, **kwargs):
    return json.dumps(NODEDATA)


def Start(dlg_id: str = 'dlg1'):
    graph = DB['dlgs'].get(dlg_id, None)
    DLGSYSTEM.data = DlgGraph(**graph) if graph else None
    DLGSYSTEM.dispatch({'event_type': 'DLG_START', 'data': DLGSYSTEM.data})


def Select(index: str):
    try:
        index = int(index)
    except ValueError:
        index = 0

    DLGSYSTEM.dispatch({'event_type': 'DLG_SELECT',
                        'data': DLGSYSTEM.data, 'index': index})


@handler('DLG_START')
def dlgStart(event, context: System):
    graph: DlgGraph = event.get('data', None)
    if isinstance(graph, DlgGraph):
        graph.reset()
        SendEvent('DLG_START')
        return {'event_type': 'DLG_UPDATE', 'data': graph}

    return {'event_type': 'DLG_END', 'data': {}}


@handler('DLG_SELECT')
def dlgSelect(event, context: System):
    graph: DlgGraph = event.get('data', None)
    index = event.get('index', 0)

    if graph:
        graph.next(index)
        return {'event_type': 'DLG_UPDATE', 'data': graph}

    return


@handler('DLG_UPDATE')
def dlgUpdate(event, context: System):
    graph: DlgGraph = event.get('data', None)
    if graph and graph.node:
        if hasattr(graph.node, 'responses'):
            # node = graph.node.copy()
            # node['responses'] = graph.node.responses
            NODEDATA['responses'] = graph.node.responses
            SendEvent(
                'DLG_RESPONSE', "")

            return

        if hasattr(graph.node, 'text'):
            NODEDATA['speaker'] = graph.node.speaker
            NODEDATA['text'] = graph.node.text
            NODEDATA['responses'] = []
            SendEvent('DLG_LINE', json.dumps(graph.node))

            return

        context.dispatch({'event_type': 'DLG_SELECT', 'data': graph})
        return

    return {'event_type': 'DLG_END'}


@handler('DLG_END')
def dlgEnd(*args, **kwargs):
    NODEDATA['speaker'] = ''
    NODEDATA['text'] = ''
    NODEDATA['responses'] = []
    SendEvent('DLG_END')


DLGSYSTEM.handlers = (dlgStart, dlgSelect, dlgUpdate, dlgEnd)
