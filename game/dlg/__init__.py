import os
from .graph import DlgGraph
from ..ecs import System, handler, EVENT_NONE
from ..db import loadDB


def loadDlgTables(filepath='dlg.db'):
    dbpath = os.path.abspath(os.path.dirname(
        os.path.realpath(__file__)) + f'/{filepath}')

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
