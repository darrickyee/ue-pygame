from typing import List, Dict, Any
from abc import ABC, abstractmethod
#from ..utils import omit


class Edge():

    def __init__(self, from_id: str, to_id: str, text: str = '', condition=None):
        self.from_id = from_id
        self.to_id = to_id
        self.text = text
        self.condition = condition or True


class AbstractNode(ABC):

    def __init__(self, node_id: str, edges: List[Dict[str, Any]] = None, **kwargs):
        self.node_id = node_id
        self.edges = edges or []

    @abstractmethod
    def next(self, index=0):
        pass

    def as_dict(self):
        return {'node_id': self.node_id, 'edges': self.edges}

    def __repr__(self):
        return f'{self.__class__.__name__} < {str(self.as_dict())} >'


class DlgText(AbstractNode):

    def __init__(self, node_id, edges=None, text='', **kwargs):
        super().__init__(node_id, edges)
        self.text = text

    def next(self, index=0):
        return self.edges[0].get('to_id', None) if self.edges else None

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
        return self.validEdges[index].get('to_id', None) if self.validEdges and index < len(self.validEdges) else None


class DlgBranch(AbstractNode):

    def next(self, index=0):
        for edge in self.edges:
            if edge.get('condition', False) or edge == self.edges[-1]:
                return edge.get('to_id', None)

        return None
