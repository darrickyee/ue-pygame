from typing import Any
from abc import ABC, abstractproperty
from collections.abc import Hashable, Iterable, Mapping, MutableSequence, Sequence
from functools import singledispatchmethod


class BaseView(Mapping, ABC):

    def __init__(self, graph):
        self._graph = graph
        self._map: dict[Any, dict] = graph._map

    @abstractproperty
    def _data(self) -> dict:
        return dict()

    @abstractproperty
    def _keys(self) -> Sequence:
        return tuple()

    @property
    def _d(self):
        return {key: self._data.get(key, None) for key in self._keys}

    def __len__(self):
        return len(self._d)

    def __iter__(self):
        return iter(self._d)

    def __getitem__(self, key):
        return self._d.get(key, None)

    def __setitem__(self, key, value):
        if key in self._d:
            self._data[key] = value
        else:
            raise KeyError(key)

    def __repr__(self):
        return f'{self.__class__.__name__}<{list(self._d)}>'


class EdgeView(BaseView):

    @property
    def _data(self):
        return {(n1, n2): self._map[n1].get(n2, None) for n1, n2 in self._keys}

    def __setitem__(self, key, value):
        if key in self._d:
            self._map[key[0]][key[1]] = value
        else:
            raise KeyError(key)

    @property
    def _keys(self):
        return ((n1, n2) for n1 in self._map for n2 in self._map[n1])

    def __contains__(self, obj):
        if isinstance(obj, Hashable):
            return super().__contains__(obj)

        if isinstance(obj, Sequence):
            return super().__contains__(tuple(obj))

        return False


class NodeView(BaseView):

    @property
    def _data(self):
        return self._graph._nodedata  # pylint: disable=protected-access

    @property
    def _keys(self):
        return (node for node in self._map)


class Graph:

    def __init__(self, *, nodes=None, edges=None):
        self._map: dict[Any, dict[Any, Any]] = {}
        self._nodedata: dict[Any, Any] = {}

        if nodes:
            self.add_nodes(nodes)

        if edges:
            self.add_edges(edges)

        self.nodes = NodeView(self)
        self.edges = EdgeView(self)

    def add_node(self, node, data=None):
        if node is not None:
            if node not in self._map:
                self._map[node] = {}

            if data is not None:
                self._nodedata[node] = data

    @singledispatchmethod
    def add_nodes(self, nodes):
        raise TypeError(
            'add_nodes() requires either an Iterable or a Mapping.')

    @add_nodes.register
    def add_nodes_mapping(self, nodemap: Mapping):
        for node, data in nodemap.items():
            self.add_node(node, data)

    @add_nodes.register
    def add_nodes_sequence(self, nodeseq: Iterable):
        for node in nodeseq:
            if isinstance(node, MutableSequence):
                self.add_node(*node[:2])
            else:
                self.add_node(node)

    def add_edge(self, node1, node2=None, data=None):
        """[summary]

        Args:
            node1 ([type]): [description]
            node2 ([type]): [description]
            data ([type], optional): [description]. Defaults to None.
        """
        if node2 is None:
            return self.add_node(node1, data)

        self.add_nodes((node1, node2))

        self._map[node1].update({node2: None})

        if data is not None:
            self._map[node1][node2] = data

    @singledispatchmethod
    def add_edges(self, edges):
        raise TypeError(
            'add_edges() requires either an Iterable or a Mapping.')

    @add_edges.register
    def add_edges_mapping(self, edgemap: Mapping):
        for edge, data in edgemap.items():
            if isinstance(edge, Iterable) and len(e := tuple(edge)) == 2:
                self.add_edge(*e[:2], data)
            else:
                raise ValueError(
                    f"add_edges(Mapping): Edge must be an Iterable with two elements (received '{edge}').")

    @add_edges.register
    def add_edges_sequence(self, edgeseq: Iterable):
        for edge in edgeseq:
            if isinstance(edge, Sequence) and len(edge) > 1:
                self.add_edge(
                    *edge[:2], None if len(edge) < 3 else edge[2])
            else:
                raise ValueError(
                    f"add_edges(Iterable): Edge must be an Iterable with at least two elements (received '{edge}').")

    def del_node(self, node):
        if node in self._map:
            del self._map[node]

        edges = tuple(edge for edge in self.edges if node in edge)
        for edge in edges:
            self.del_edge(*edge)

        self._updatedata()

    def del_edge(self, node1, node2):
        if (node1, node2) in self.edges:
            del self._map[node1][node2]

        self._updatedata()

    def _updatedata(self):
        self._nodedata = {node: data for node,
                          data in self._nodedata.items() if node in self.nodes}

    # ---- Magic/builtin methods ---- #

    def get(self, key, default=None, /):
        try:
            return self[key]
        except KeyError:
            return default

    def keys(self):
        return self._map.keys()

    def __contains__(self, obj):
        return obj in self._map

    def __getitem__(self, key):
        return self._map[key]

    def __delitem__(self, key):
        self.del_node(key)

    @singledispatchmethod
    def __setitem__(self, key, value):
        self.add_node(key, value)

    @__setitem__.register
    def __setitem__tuple(self, key: tuple, value):
        if len(key) >= 2:
            self.add_edge(*key[:2], value)
        else:
            self.add_node(key, value)

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return f"{self.__class__.__name__}(nodes={dict(self.nodes)}, edges={dict(self.edges)})"

    # ---- Utilities ---- #

    def clear(self):
        self._map.clear()
        self._nodedata.clear()

    def copy(self):
        return Graph(nodes=self.nodes, edges=self.edges)

    def subgraphof(self, other):
        return all(node in other
                   for node in self.nodes) and all(edge in other.edges
                                                   for edge in self.edges)

    def equalto(self, other):
        return self.subgraphof(other) and other.subgraphof(self)

    def to_json(self):
        return {'nodes': dict(self.nodes), 'edges': dict(self.edges)}
