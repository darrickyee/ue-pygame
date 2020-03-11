from typing import List


class Edge(dict):

    def __init__(self, from_id: str, to_id: str, text: str = '', condition=True, **kwargs):
        super().__init__(from_id=from_id, to_id=to_id, text=text, condition=condition)


class Node(dict):

    defaults = {}

    def __init__(self, node_id: str, edges: List[Edge] = None, **kwargs):
        super().__init__(node_id=node_id, edges=edges or [])
        self.update({k: kwargs.get(k, None) or v
                     for k, v in self.__class__.defaults.items()})

    def __getattr__(self, name):
        if name in self:
            return self[name]

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def __setattr__(self, name, value):
        if name in self:
            self[name] = value
            return

        raise AttributeError(
            f"'{self.__class__.__name__}' object has no attribute '{name}'")

    def next(self, index=0) -> str:
        if self.edges:
            index = min(max(0, index), len(self.edges)-1)
            return self.edges[index].get('to_id', None)

        return None

    def __repr__(self):
        return f'{self.__class__.__name__} { {k: v for k, v in self.items()} }'


class DlgLine(Node):

    defaults = {'text': '', 'speaker': ''}

    def next(self, index=0) -> str:
        return super().next(0)


class _DlgCond(Node):

    @property
    def edges(self) -> List[Edge]:
        return tuple(edge for edge in self['edges'] if edge.get('condition', True))


class DlgBranch(_DlgCond):

    def next(self, index=0) -> str:
        return super().next(0)


class DlgResponse(_DlgCond):

    @property
    def responses(self) -> List[str]:
        return tuple(edge.get('text', '') for edge in self.edges)
