from typing import List, Dict
from .node import AbstractNode, DlgText, DlgResponse, DlgBranch
from ..utils import omit


NODE_CLASS = {
    'text': DlgText,
    'response': DlgResponse,
    'branch': DlgBranch
}

NODE_TYPE = {v: k for k, v in NODE_CLASS.items()}


class DlgGraph:

    def __init__(self, root_id, nodelist: List[AbstractNode] = None):
        self.nodelist = nodelist
        self.root_id = root_id

    @property
    def nodes(self):
        return {node.node_id: node for node in self.nodelist if isinstance(node, AbstractNode)}

    def getNode(self, node_id):
        return self.nodes.get(node_id, None)


def dlgNode(node_type, *args, **kwargs):
    return NODE_CLASS.get(node_type, DlgText)(*args, **kwargs)


def exportGraph(nodelist: List[AbstractNode]) -> Dict[str, List]:
    _nodes = [{'node_type': NODE_TYPE.get(type(
        node), 'UNKNOWN'), **omit(['edges'], node.as_dict())} for node in nodelist]

    _edges = [{'from_id': node.node_id, **edge}
              for node in nodelist for edge in node.edges]

    return {'nodes': _nodes, 'edges': _edges}


def importGraph(nodes: List[Dict], edges: List[Dict]) -> List[AbstractNode]:

    _nodes = [NODE_CLASS.get(node.get('node_type', None), DlgText)(
        **node) for node in nodes]

    for node in _nodes:
        node.edges = [omit(['from_id'], edge)
                      for edge in edges if edge.get('from_id') == node.node_id]

    return _nodes
