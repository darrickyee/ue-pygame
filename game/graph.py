# %%
import typing as t


class Graph:

    def __init__(self):
        self._graph: t.Dict[t.Any, t.Dict[t.Any, t.Dict[str, t.Any]]] = {}

    @property
    def nodes(self):
        return tuple(self._graph.keys())

    @property
    def edges(self):
        return tuple((n1, n2) for n1 in self._graph for n2 in self._graph[n1])

    def addNode(self, node):
        if node not in self._graph:
            self._graph[node] = {}

    def addEdge(self, from_node, to_node, edge_data=None):
        """Adds an edge.  If the edge already exists, its data is replaced by `edge_data`.
        Nodes that are not already in the graph are automatically added.

        Args:
            `from_node` ([type]): [description]
            `to_node` ([type]): [description]
        """
        for node in from_node, to_node:
            self.addNode(node)

        self._graph[from_node][to_node] = edge_data

    def removeNode(self, node):
        if node in self.nodes:
            del self._graph[node]

        for child_nodes in self._graph.values():
            if node in child_nodes:
                del child_nodes[node]

    def removeEdge(self, from_node, to_node):
        if (from_node, to_node) in self.edges:
            del self._graph[from_node][to_node]

    def children(self, node):
        return tuple(self._graph.get(node, ()))

    def parents(self, node):
        return tuple(p for p, c in self.edges if c == node)

    # ---- Magic methods ---- #

    def __contains__(self, obj):
        try:
            return obj in self.nodes
        except TypeError:
            return False

    def __getitem__(self, key):
        try:
            return dict(self._graph[key])
        except KeyError:
            return None

    def __setitem__(self, key, value):
        pass

    def __delitem__(self, key):
        pass

    def __iter__(self):
        return iter(self._graph)

    def __len__(self):
        return len(self._graph)

    def __repr__(self):
        return f"{self.__class__.__name__} <nodes={len(self)}, edges={len(self.edges)}>"
