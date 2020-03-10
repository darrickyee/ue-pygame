import os
from .graph import DlgGraph, importGraph
from ..db import loadDB
from ..ecs import System, handler, EVENT_NONE


def getResponse(context):
    sel = input()
    try:
        sel = int(sel)
    except ValueError:
        sel = 1

    DISPATCH({'event_type': 'DLG_ONRESPONSE', 'data': sel-1}, context)


# %%
DLGSYS = System()


DISPATCH = DLGSYS.dispatch


@handler('DLG_UPDATE')
def readNode(event, context: DlgGraph):
    if isinstance(context, DlgGraph):
        currnode = context.currnode

        if currnode:
            if hasattr(currnode, 'responses'):
                DISPATCH({'event_type': 'DLG_RESPONSE',
                          'data': currnode.responses}, context)
                return None

            if hasattr(currnode, 'text'):
                DISPATCH({'event_type': 'DLG_LINE',
                          'data': currnode}, context)
                return None

            context.currnode = context.getNode(currnode.next())
            DISPATCH(event, context)


@handler('DLG_RESPONSE')
def dlgResponse(event, context: DlgGraph):
    for i, resp in enumerate(event['data']):
        print(f'[{i+1}]\t{resp}')


@handler('DLG_LINE')
def dlgText(event, context: DlgGraph):
    print(f"{event['data']['speaker']}:\t{event['data']['text']}")


@handler(('DLG_RESPONSE', 'DLG_LINE'))
def dummyGetResp(event, context: DlgGraph):
    getResponse(context)


@handler('DLG_ONRESPONSE')
def dlgSelect(event, context: DlgGraph):
    context.currnode = context.getNode(
        context.currnode.next(event['data']))
    DISPATCH({'event_type': 'DLG_UPDATE'}, context)


LOG = []


@handler()
def logEvent(event, context):
    LOG.append(event)


DLGSYS.handlers = (dlgSelect, dlgResponse, dlgText,
                   dummyGetResp, readNode, logEvent)


DB_PATH = os.path.abspath(os.path.dirname(
    os.path.realpath(__file__)) + '/dlg.db')


tbls = loadDB(DB_PATH)


def loadDlgGraphs(dlg_graphs, dlg_nodes, dlg_edges):
    graphs = {}
    for graph_row in dlg_graphs:
        gid = graph_row.get('graph_id', None)
        nodes_edges = [[row for row in rows if row['graph_id'] == gid]
                       for rows in (dlg_nodes, dlg_edges)]
        graphs[gid] = DlgGraph(
            graph_row['root_id'], importGraph(*nodes_edges))

    return graphs


dlgs = loadDlgGraphs(**tbls)


# %%


def displayDlg(text, responses):
    if text:
        print(text)

    for i, resp in enumerate(responses):
        print(f'[{i+1}]\t{resp}')

    sel = input()
    try:
        sel = min(max(0, int(sel)-1), len(responses)-1)
    except ValueError:
        sel = 0

    return sel


def playDlg(graph: DlgGraph):

    # currnode = graph.getNode(graph.root_id)
    # nextidx = 0

    # while currnode:
    #     text = currnode.text if hasattr(currnode, 'text') else None
    #     responses = currnode.responses if hasattr(
    #         currnode, 'responses') else []

    #     if text or responses:
    #         nextidx = displayDlg(text, responses)

    #     currnode = graph.getNode(currnode.next(nextidx))
    print('Playing...')
    DISPATCH({'event_type': 'DLG_UPDATE'}, graph)
