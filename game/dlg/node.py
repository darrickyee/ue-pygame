import json
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class AbstractNode(ABC):

    def __init__(self, key: str, edges: List[Dict[str, Any]] = None):
        self.key = key
        self.edges = edges or []

    @abstractmethod
    def next(self, index=0):
        pass

    def as_dict(self):
        return {'key': self.key, 'edges': self.edges}

    def __repr__(self):
        return f'{self.__class__.__name__}< {str(self.as_dict())} >'


class DlgText(AbstractNode):

    def __init__(self, key, edges=None, text=''):
        super().__init__(key, edges)
        self.text = text

    def next(self, index=0):
        return self.edges[0].get('key', None) if self.edges else None

    def as_dict(self):
        return {**super().as_dict(), 'text': self.text}


class DlgResponse(AbstractNode):

    @property
    def validEdges(self) -> List[Dict[str, Any]]:
        return [edge for edge in self.edges if edge.get('condition', True)]

    @property
    def responses(self) -> List[str]:
        return [edge.get('text', None) for edge in self.validEdges]

    def next(self, index=0):
        return self.validEdges[index].get('key', None) if self.validEdges and index < len(self.validEdges) else None


class DlgBranch(AbstractNode):

    def next(self, index=0):
        for edge in self.edges:
            if edge.get('condition', False) or edge == self.edges[-1]:
                return edge.get('key', None)

        return None


def omit(key, d: Dict):
    _d = d.copy()
    if key in _d:
        del _d[key]

    return _d


class DlgGraph:

    nodetypes = {
        DlgText: 'text',
        DlgResponse: 'response',
        DlgBranch: 'branch'
    }

    def __init__(self, rootkey, nodelist: List[AbstractNode] = None):
        self.nodes = self._loadNodes(rootkey, nodelist or [])

    def _loadNodes(self, key, nodelist: List[AbstractNode]):
        nodes = {
            node.key: node for node in nodelist if isinstance(node, AbstractNode)}
        nodes['root'] = nodes[key]
        return nodes

    def export(self):
        nodes = [{'nodetype': self.__class__.nodetypes.get(type(
            node), 'UNKNOWN'), **omit('edges', node.as_dict())} for node in self.nodes.values()]
        edges = [{'fromkey': node.key, **edge}
                 for node in self.nodes.values() for edge in node.edges]
        return {'nodes': nodes, 'edges': edges}

    def getNode(self, key):
        return self.nodes.get(key, None)


def importGraph(nodes, edges):
    ntypes = dict(map(lambda x: x[::-1], self.__class__.nodetypes.items()))
    _nodes = [ntypes[n['nodetype']](**omit('nodetype', n)) for n in nodes]
    return _nodes


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


def playDlg(graph):

    currnode = graph['0']
    nextidx = 0

    while currnode:
        text = currnode.text if hasattr(currnode, 'text') else None
        responses = currnode.responses if hasattr(
            currnode, 'responses') else []

        if text or responses:
            nextidx = displayDlg(text, responses)

        currnode = graph.get(currnode.next(nextidx), None)
