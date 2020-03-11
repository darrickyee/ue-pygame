import os
import json
import ue_pylink
from .db import loadDB
from .dlg import dlgs, playDlg, DISPATCH, DLGSYS, DlgGraph
from .ecs import handler, System

DB_PATH = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/game.db')

DB = loadDB(DB_PATH)

# ue_pylink.broadcast('Init', 'Go')  # pylint: disable=no-member


def getGameEntity(entityid: str):
    return json.dumps(DB['npcs'].get(entityid, {}))


GRAPH = dlgs['dlg1']


def Select(index: str):
    try:
        index = int(index)
    except ValueError:
        index = 1

    DISPATCH({'event_type': 'DLG_SELECT', 'data': GRAPH, 'index': index-1})


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
            ue_pylink.broadcast(
                'DLG_RESPONSE', json.dumps(graph.node.responses))
            return

        if hasattr(graph.node, 'text'):
            ue_pylink.broadcast('DLG_LINE', json.dumps(
                {'speaker': graph.node.speaker, 'text': graph.node.text}))
            return

        context.dispatch({'event_type': 'DLG_SELECT', 'data': graph})
        return


DLGSYS.handlers = (dlgSelect, dlgUpdate)

playDlg(dlgs['dlg1'])
