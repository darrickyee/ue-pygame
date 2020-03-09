from typing import List, Dict, Any
from abc import ABC, abstractmethod


class AbstractNode(ABC):

    def __init__(self, nodeid: str, edges: List[Dict[str, Any]] = None):
        self.nodeid = nodeid
        self.edges = edges or []

    @abstractmethod
    def next(self, index=0):
        pass

    def as_dict(self):
        return {'nodeid': self.nodeid, 'edges': self.edges}


class DlgText(AbstractNode):

    def __init__(self, nodeid, edges=None, text=''):
        super().__init__(nodeid, edges)
        self.text = text

    def next(self, index=0):
        return self.edges[0].get('node', None) if self.edges else None

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
        return self.validEdges[index].get('node', None) if self.validEdges and index < len(self.validEdges) else None


class DlgBranch(AbstractNode):

    def next(self, index=0):
        for edge in self.edges:
            if edge.get('condition', False) or edge == self.edges[-1]:
                return edge.get('node', None)

        return None


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
