# %%
from functools import reduce
from typing import List, Dict, Any
from abc import ABC, abstractmethod


class AbstractNode(ABC):

    def __init__(self, nodeid: str, edges: List[Dict[str, Any]] = None):
        self.nodeid = nodeid
        self.edges = edges or []

    @abstractmethod
    def next(self, index=0):
        pass


class DlgText(AbstractNode):

    def __init__(self, nodeid, edges=None, text=''):
        super().__init__(nodeid, edges)
        self.text = text

    def next(self, index=0):
        return self.edges[0].get('node', None) if self.edges else None


class DlgResponse(AbstractNode):

    def __init__(self, nodeid, edges=None):
        super().__init__(nodeid, edges)

    @property
    def validEdges(self) -> List[Dict[str, Any]]:
        return [edge for edge in self.edges if edge.get('condition', True)]

    @property
    def responses(self) -> List[str]:
        return [edge.get('text', None) for edge in self.validEdges]

    def next(self, index=0):
        return self.validEdges[index].get('node', None) if self.validEdges and index < len(self.validEdges) else None


class DlgBranch(AbstractNode):

    def __init__(self, nodeid, edges=None):
        super().__init__(nodeid, edges)

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

# %%


dt0 = DlgText('dt0', text='Hi!', edges=[{'node': 'dt1'}])
dt1 = DlgText('dt1', edges=[{'node': 'dr1'}], text='H ow are you!')
dr1 = DlgResponse('dr1', [{'node': 'dt2', 'text': 'Fyne'}, {
                  'node': 'dt3', 'text': 'Bad'}, {
                  'node': 'dt3', 'text': 'Ok', 'condition': True}])
dt2 = DlgText('dt2', text='Gewd!', edges=[{'node': 'db1'}])
dt3 = DlgText('dt3', [{'node': 'dt0'}], text='Try again!')

db1 = DlgBranch('db1', edges=[{'node': 'dt0', 'condition': True}, {
                'node': 'dt1', 'condition': False}])s

dg = {n.nodeid: n for n in (dt0, dt1, dr1, dt2, dt3, db1)
      }
dg['0'] = dt0

# %%


class DlgPlayer():

    def __init__(self, graph):
        self.graph = graph
        self.currnode = graph['0']

    def start(self):
        if hasattr(self.currnode, 'responses'):
            displayResponses(self.currnode.responses)
        elif hasattr(self.currnode, 'text'):
            displayText(self.currnode.text)
        else:
            self.currnode = self.graph[self.currnode.next()]


class System():

    def __init__(self, handlers: List = None):
        self.handlers = handlers or []

    def _gethandler(self, handler):
        if hasattr(handler, 'process'):
            return handler.process

        return handler

    def process(self, event, context=None):
        context = context or self
        return reduce(lambda event, handler: self._gethandler(handler)(event, context), self.handlers, event)


def hndlr1(event, context):
    print(event)
    print(context)
    return event


def hndlr2(event, context):

    event['text'] = 'Processed ' + event['text']
    return event


subsys = System([hndlr2, hndlr1])
