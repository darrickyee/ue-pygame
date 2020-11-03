from pathlib import Path
from ..db import loadDB
from .dialogue import Dialogue
from .nodes import DlgBranch, DlgEnd, DlgGroup, DlgNode, DlgText


def loadDlgTables(filepath='dlg.db'):
    dbpath = Path(__file__).parent / filepath

    return loadDB(dbpath)


def importDlgData(dlg_graphs, dlg_nodes, dlg_edges):
    graphs = {}
    for graph_row in dlg_graphs:
        gid = graph_row.get('graph_id', None)
        nodes_edges = [[row for row in rows if row['graph_id'] == gid]
                       for rows in (dlg_nodes, dlg_edges)]
        graphs[gid] = {'root_id': graph_row['root_id'],
                       'node_data': nodes_edges[0],
                       'edge_data': nodes_edges[1]}
    return graphs


def loadDlgGraphs(filepath='dlg.db'):
    return importDlgData(**loadDlgTables(filepath))
