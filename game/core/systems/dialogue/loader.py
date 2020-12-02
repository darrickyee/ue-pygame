from typing import Any, Tuple
from ....lib import Graph
from ....lib.util import pick
from .nodes import DlgBranch, DlgEnd, DlgGroup, DlgNode, DlgText

NODE_TYPES = {
    'branch': DlgBranch,
    'end': DlgEnd,
    'group': DlgGroup,
    'text': DlgText
}


def loadNodes(node_list: list[dict[str, Any]]):
    node_map = {}
    for node in node_list:
        try:
            node_map.update({node['node_id']:
                             NODE_TYPES[node['node_type']](**pick(['condition', 'on_enter', 'text', 'speaker'], node))})
        except (KeyError, TypeError) as err:
            print(err)
            return {}

    return node_map


def loadDlgGraph(node_data: list[dict[str, Any]], edge_data: list[tuple]):
    nodes = loadNodes(node_data)
    if nodes:
        edges = [(nodes[src_id], nodes[dst_id], data[0] if data else None)
                 for src_id, dst_id, *data in edge_data]
        return Graph(nodes=nodes.values(), edges=edges)

    return None
