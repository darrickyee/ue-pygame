from .graph import DlgGraph
from ..ecs import System, handler, EntityManager, EVENT_NONE

START_EVENT = {'event_type': 'DLG_START', 'dlg_id': 'dlg1'}

DLGREADER = {
    'node': {'text': '', 'responses': []},
    'dlg_id': '',
    'graph': None
}


class DlgSystem(System):

    def __init__(self, entitymgr: EntityManager):
        super().__init__(handlers=(self._start, self._select,
                                   self._update, self._end), entitymgr=entitymgr)
        self.dlg = self.entitymgr.getEntity('player')['dlg_reader']

    @handler('DLG_START')
    def _start(self, event, context: System):
        if not event.get('dlg_id', None):
            return EVENT_NONE

        self.graph.reset()
        SendEvent('DLG_START')
        return {'event_type': 'DLG_UPDATE', 'data': graph}

        return {'event_type': 'DLG_END', 'data': {}}

    @handler('DLG_SELECT')
    def _select(self, event, context: System):
        graph: DlgGraph = event.get('data', None)
        index = event.get('index', 0)

        if graph:
            graph.next(index)
            return {'event_type': 'DLG_UPDATE', 'data': graph}

        return

    @handler('DLG_UPDATE')
    def _update(self, event, context: System):
        graph: DlgGraph = event.get('data', None)
        if graph and graph.node:
            if hasattr(graph.node, 'responses'):
                # node = graph.node.copy()
                # node['responses'] = graph.node.responses
                NODEDATA['responses'] = graph.node.responses
                SendEvent(
                    'DLG_RESPONSE', "")

                return

            if hasattr(graph.node, 'text'):
                NODEDATA['speaker'] = graph.node.speaker
                NODEDATA['text'] = graph.node.text
                NODEDATA['responses'] = []
                SendEvent('DLG_LINE', json.dumps(graph.node))

                return

            context.dispatch({'event_type': 'DLG_SELECT', 'data': graph})
            return

        return {'event_type': 'DLG_END'}

    @handler('DLG_END')
    def _end(*args, **kwargs):
        NODEDATA['speaker'] = ''
        NODEDATA['text'] = ''
        NODEDATA['responses'] = []
        SendEvent('DLG_END')
