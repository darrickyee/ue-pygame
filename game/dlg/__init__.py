from .node import DlgGraph, importGraph
from ..db import loadDB


tbls = loadDB('dlg.db')


def loadDlgGraphs(dlg_graphs, dlg_nodes, dlg_edges):
    graphs = {}
    for graph_row in dlg_graphs:
        gid = graph_row.get('graph_id', None)
        node_rows = [row for row in dlg_nodes if row['graph_id'] == gid]
        edge_rows = [row for row in dlg_edges if row['graph_id'] == gid]
        graphs[gid] = DlgGraph(
            graph_row['root_id'], importGraph(node_rows, edge_rows))

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

    currnode = graph.getNode(graph.root_id)
    nextidx = 0

    while currnode:
        text = currnode.text if hasattr(currnode, 'text') else None
        responses = currnode.responses if hasattr(
            currnode, 'responses') else []

        if text or responses:
            nextidx = displayDlg(text, responses)

        currnode = graph.getNode(currnode.next(nextidx))
