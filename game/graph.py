# %%
import typing as t
from abc import abstractproperty
from collections.abc import Hashable, Iterable, Mapping, MutableSequence, Sequence
from functools import singledispatchmethod

startdict = {'a': {'b': 2}, 2: {'c': 'd'}}

# %%


class BaseView(Mapping):

    def __init__(self, graph):
        self._graph = graph
        self._map: t.Dict[t.Any, t.Dict[t.Any, t.Any]] = graph._map

    @abstractproperty
    def _data(self):
        pass

    @abstractproperty
    def _keys(self):
        pass

    @property
    def _d(self):
        return {key: self._data.get(key, None) for key in self._keys}

    def __len__(self):
        return len(self._d)

    def __iter__(self):
        return iter(self._d)

    def __getitem__(self, key):
        return self._d[key]

    def __setitem__(self, key, value):
        if key in self._d:
            self._data[key] = value
        else:
            raise KeyError(key)

    def __repr__(self):
        return f'{self.__class__.__name__}<{self._d}>'


class EdgeView(BaseView):

    @property
    def _data(self):
        return self._graph._edgedata

    @property
    def _keys(self):
        return ((n1, n2) for n1 in self._map for n2 in self._map[n1])

    def __contains__(self, obj):
        if isinstance(obj, Hashable):
            return super().__contains__(obj)

        if isinstance(obj, Iterable):
            return super().__contains__(tuple(obj))

        return False


class NodeView(BaseView):

    @property
    def _data(self):
        return self._graph._nodedata

    @property
    def _keys(self):
        return (node for node in self._map)

    def __add__(self, other):
        self._graph.add_node(other)

# %%


class Graph:

    def __init__(self, **kwargs):
        self._map: t.Dict[t.Any, t.Dict[t.Any, t.Any]] = {}
        self._nodedata: t.Dict[t.Any, t.Any] = {}
        self._edgedata: t.Dict[t.Tuple, t.Any] = {}
        self.data = kwargs

        self.nodes = NodeView(self)
        self.edges = EdgeView(self)

        self.clear = self._map.clear

    def add_node(self, node, data=None):
        if node is not None:
            if node not in self._map:
                self._map[node] = {}

            if data is not None:
                self.nodes[node] = data

    @singledispatchmethod
    def add_nodes(self, nodes):
        raise TypeError(
            'add_nodes() requires either an Iterable or a Mapping.')

    @add_nodes.register
    def add_nodes_graph(self, graph: Graph):
        for node, data in graph.nodes.items():
            self.add_node(node, data)

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

    def add_edge(self, node1, node2, data=None):
        """[summary]

        Args:
            node1 ([type]): [description]
            node2 ([type]): [description]
            data ([type], optional): [description]. Defaults to None.
        """
        self.add_nodes((node1, node2))

        self._map[node1].update({node2: None})

        if data is not None:
            self.edges[node1, node2] = data

    @singledispatchmethod
    def add_edges(self, edges):
        raise TypeError(
            'add_edges() requires either an Iterable or a Mapping.')

    @add_edges.register
    def add_edges_mapping(self, edgemap: Mapping):
        for edge, data in edgemap.items():
            if isinstance(edge, Iterable) and len(e := tuple(edge)) == 2:
                self.add_edge(*edge[:2], data)
            else:
                raise ValueError(
                    f"add_edges(Mapping): Edge must be an Iterable with two elements (received '{edge}').")

    @add_edges.register
    def add_edges_sequence(self, edgeseq: Iterable):
        for edge in edgeseq:
            if isinstance(edge, Iterable) and len(edge) > 1:
                self.add_edge(
                    *edge[:2], data=None if len(edge) < 3 else edge[2])
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

        self._edgedata = {edge: data for edge,
                          data in self._edgedata.items() if edge in self.edges}

    # ---- Magic methods ---- #

    def __contains__(self, obj):
        return obj in self._map

    def __getitem__(self, key):
        return {k: self.edges[key, k] for k in self._map[key]}

    def __delitem__(self, key):
        self.del_node(key)

    def __iter__(self):
        return iter(self._map)

    def __len__(self):
        return len(self._map)

    def __repr__(self):
        return f"{self.__class__.__name__} <nodes={len(self)}, edges={len(self.edges)}>"

    def items(self):
        return list((k, self[k]) for k in self._map)


# %%
g = Graph()
g.add_edge('a1', 'a2', data='My edge data')
g.add_edge('n1', 'n2', data='More data')
# %%


class MyObj:
    def __init__(self, value):
        self.value = value

# %%
