class DlgPlayer:

    def __init__(self, graph: Graph, context: Any = None) -> None:
        self._graph = graph
        self._context = context or {}

    @property
    def condition(self):
        if self._context:
            return predicate.bind_data(self._context)

        return lambda _: True

    def _childdata(self, node: DlgNode):
        child_data = list()
        for child in self._graph.get(node, []):
            if not child.conditions or all(self.condition(cond)
                                           for cond in child.conditions):
                if isinstance(child, DlgGroup):
                    child_data += self._childdata(child)
                else:
                    child_data += [(child, self._graph[node][child])]

        return child_data

    def view(self, node: DlgNode) -> Dict[str, Any]:
        nodes, responses = tuple(), tuple()

        if (child_data := self._childdata(node)):
            nodes, responses = tuple(zip(*child_data))

        return {'node': node,
                'children': nodes,
                'responses': responses,
                'context': self._context} if node else {}

    def transition(self, node: DlgNode, fsm_input=None):
        fsm_input = fsm_input or 0
        if children := self.view(node).get('children', []):
            return children[fsm_input if fsm_input < len(children) else 0]

        return None

    def action(self, event: dict[str, Any]) -> None:
        if event.get('event_type', None) == 'ENTER':
            return self._action(event.get('state', None), event)

    @singledispatchmethod
    def _action(self, node, event):
        print('Dialogue ended.')

    @_action.register
    def _action_DlgText(self, node: DlgText, event):
        print(f'{node.speaker}: {node.text}')
        for i, response in enumerate(self.view(node)['responses']):
            print(f'{i}. {response}')

        sym = input('Enter a response: ')
        try:
            sym = int(sym)
        except ValueError:
            sym = 0

        event['target'].next(sym)

    @_action.register
    def _action_DlgBranch(self, node: DlgBranch, event):
        event['target'].next()
