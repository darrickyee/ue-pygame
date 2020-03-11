from typing import List, Dict
from .node import Node, DlgLine, DlgResponse, DlgBranch
from ..utils import omit


NODE_CLASS = {
    'line': DlgLine,
    'response': DlgResponse,
    'branch': DlgBranch
}

NODE_TYPE = {v: k for k, v in NODE_CLASS.items()}


class DlgGraph:

    def __init__(self, root_id, nodelist: List[Node] = None):
        self.nodelist = nodelist
        self.root_id = root_id
        self.node = self.getNode(root_id)

    @property
    def nodes(self):
        return {node.node_id: node for node in self.nodelist if isinstance(node, Node)}

    def getNode(self, node_id) -> Node:
        return self.nodes.get(node_id, None)

    def next(self, index=0):
        if self.node:
            self.node = self.nodes.get(self.node.next(index), None)

        return self.node


def exportGraph(nodelist: List[Node]) -> Dict[str, List]:
    _nodes = [{'node_type': NODE_TYPE.get(type(
        node), 'UNKNOWN'), **omit(['edges'], node)} for node in nodelist]

    _edges = [{'from_id': node.node_id, **edge}
              for node in nodelist for edge in node['edges']]

    return {'nodes': _nodes, 'edges': _edges}


def importGraph(nodes: List[Dict], edges: List[Dict]) -> List[Node]:

    _nodes = [NODE_CLASS[node.get('node_type', 'line')](
        **node) for node in nodes]

    for node in _nodes:
        node.edges = [{k: v for k, v in omit(['from_id', 'graph_id'], edge).items()
                       if v is not None}
                      for edge in edges if edge.get('from_id') == node.node_id]

    return _nodes
