# %%
# Needed for interactive window relative import
import sys
from pathlib import Path
import jsonpatch as jp
import rx.operators as ops
from rx.subject import Subject

sys.path[0] = str(Path(sys.path[0]).parent)  # nopep8
from game.graph import Graph


# %%

def cond(conddata):
    return True


class Dialogue:

    def __init__(self, graph: Graph):
        self.graph = graph
        self._node = None

    @property
    def node(self):
        return self._node

    def start(self):
        startnode = [node for node, data in self.graph.nodes.items()
                     if data == 'root'] or list(self.graph.nodes)

        if startnode:
            self._node = startnode[0]
        else:
            raise ValueError(
                f"Dialogue.start() failed: Graph '{self.graph}' has no nodes.")

    def children(self):
        if self.graph[self.node]:
            return [node for node, edgedata in self.graph[self.node].items() if self.validate(edgedata)]

        return []

    def validate(self, edgedata):
        return edgedata is None or cond(edgedata)

    def next(self, response=0):
        children = self.children()

        if children:
            self._node = children[response] if len(
                children) > response else children[0]
            return self.node

        return None

        # %%


class DlgGraph(Graph):

    def __init__(self, edges=None):
        super().__init__()
        if edges:
            for edge in edges:
                self.add_edge(*edge)

    @property
    def root(self):
        if self.nodes:
            return self.nodes[0]

        return None

    def subgraph(self, node):
        if node not in self:
            if isinstance(node, int) and node < len(self.nodes):
                node = self.nodes[node]
            else:
                raise ValueError(f'Node {node} not found')

        edges = (edge for edge in self.edges if edge[0] in self.children(node))

        return type(self)(edges)


class DlgNode:

    def __repr__(self):
        return f"{type(self).__name__}()"

    def action(self, graph: Graph, context: dict):
        pass


class DlgText(DlgNode):

    def __init__(self, text='', speaker=None):
        self.text = text
        self.speaker = speaker or ''

    def action(self, graph: Graph, context):
        edges = []
        for child, data in graph[self].items():
            if not isinstance(data, dict) or data.get('condition', True):
                edges.append((child, data or {}))

        context['text'] = self.text
        context['children'] = [e[0] for e in edges]
        context['options'] = [e[1].get('text', e[0].text) for e in edges]

    def __repr__(self):
        return f"{type(self).__name__}(text='{self.text}')"


class DlgBranch(DlgNode):
    pass

# %%


r = DlgText('Hi')
b1 = DlgBranch()
c1 = DlgText('How  r u?')
c2 = DlgText('R u ok?')
c_1 = DlgText('Ohai im fyne')
G = DlgGraph([(r, c1, {'text': 'Say something'}),
              (c1, c_1, {'text': 'Select me', 'condition': True}),
              (c1, c2),
              (c_1, b1, {'text': 'This is a branch'}),
              (b1, c2, {'condition': True}),
              (b1, r)])


# %%


def validEdge(edge):
    return not isinstance(edge[1], dict) or edge[1].get('condition', True)


class DlgReader:

    def __init__(self, graph: Graph):
        self.graph = graph
        self._subject = Subject()
        self._node = graph.root

        self.subscribe = self._subject.subscribe
        self.pipe = self._subject.pipe

    @property
    def node(self):
        return self._node

    @node.setter
    def node(self, value):
        self._node = value
        print(f'Current node is {self._node}')
        if self.node is None:
            self._subject.on_completed()
        else:
            self._subject.on_next(self)

    @property
    def text(self):
        return self.node.text

    @property
    def speaker(self):
        return self.node.speaker

    @property
    def validEdges(self):
        return [(child, data or {})
                for child, data in self.graph[self.node].items()
                if validEdge((child, data))]

    @property
    def options(self):
        return [child[1].get('text', child[0].text if hasattr(child[0], 'text') else '')
                for child in self.validEdges]

    def nextNode(self, selection=0):
        if not self.validEdges:
            return None

        selection = max(0, min(selection, len(self.validEdges)-1))
        return self.validEdges[selection][0]


def printDlg(state):
    print(f"{state.speaker or 'Speaker'}: {state.text}")
    if state.options:
        for i, option in enumerate(state.options):
            print(f"{i+1}. {option}")


inputs = Subject()


def getInput():
    opt = (int(input("Select: ") or 0)-1)
    inputs.on_next(opt)


def branchHandler(state):
    if state.validEdges:
        state.node = state.validEdges[0][0]
    else:
        state.node = None


def play(graph: DlgGraph):

    reader = DlgReader(graph)

    graph_stream = reader.pipe(ops.filter(lambda r: isinstance(r, DlgReader)))
    text_stream = graph_stream.pipe(
        ops.filter(lambda r: isinstance(r.node, DlgText)))
    branch_stream = graph_stream.pipe(
        ops.filter(lambda r: isinstance(r.node, DlgBranch)))

    print_disposer = text_stream.subscribe(printDlg)
    branch_disposer = branch_stream.subscribe(branchHandler)

    def select(opt):
        reader.node = reader.nextNode(opt)

    input_disposer = inputs.subscribe(select)

    def end():
        print_disposer.dispose()
        input_disposer.dispose()
        branch_disposer.dispose()

    reader.subscribe(on_completed=end)

    reader.node = reader.graph.root
    while reader.node:
        getInput()


# %%
play(G)

play(G)
# %%
