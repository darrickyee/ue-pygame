from typing import List, Dict
from .node import Node, DlgLine, DlgResponse, DlgBranch, Edge


NODE_CLASS = {
    'line': DlgLine,
    'response': DlgResponse,
    'branch': DlgBranch
}

NODE_TYPE = {v: k for k, v in NODE_CLASS.items()}


def buildNodes(node_data: List[Dict], edge_data: List[Dict]):
    nodes: List[Node] = [NODE_CLASS.get(data['node_type'], DlgLine)(**data)
                         for data in node_data]

    for node in nodes:
        node.edges = [
            Edge(**{k: v for k, v in data.items() if v})
            for data in edge_data if data['from_id'] == node.node_id]

    return nodes


class DlgGraph:

    def __init__(self, root_id, node_data: List[Dict], edge_data: List[Dict]):
        self.nodelist = buildNodes(node_data, edge_data)
        self.root_id = root_id
        try:
            self._node = self.nodes[root_id]
        except KeyError:
            raise ValueError(
                f"Graph initialization failed: No valid node found for root_id: '{root_id}'")

    @property
    def node(self):
        return self._node

    @property
    def nodes(self):
        return {node.node_id: node for node in self.nodelist if isinstance(node, Node)}

    def next(self, index=0):
        if self.node:
            self._node = self.nodes.get(self.node.next(index), None)

        return self.node

    def jump(self, node_id):
        if node_id in self.nodes:
            self._node = self.nodes[node_id]

    def reset(self):
        self.jump(self.root_id)
