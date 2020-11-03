from typing import Any, Callable, Union
from ..lib import Graph, StateMachine, evaluate
from ..lib.fsm import changeListener
from .nodes import DlgBranch, DlgEnd, DlgGroup, DlgNode, DlgText


class Dialogue(StateMachine):

    def __init__(self, graph: Graph, context: dict[str, Any] = None) -> None:
        self._graph = graph
        self._context = context or {}
        super().__init__(tuple(self._graph)[0], self.transition)

        self.subscribe(changeListener(self, on_enter=self._on_enter))

    def _eval(self, predicate: dict[str, Any]) -> bool:
        """Evaluates `predicate` against `self._context`.
        """
        if predicate and self._context:
            return evaluate(self._context, predicate)

        return True

    def _children(self, node: DlgNode):
        # Get only child nodes & responses that meet conditions
        children: dict[DlgNode, str] = {n: response
                                        for n, response in self._graph[node].items()
                                        if self._eval(n.condition)}

        for child in tuple(children):
            if isinstance(child, DlgGroup):
                del children[child]
                children.update(self._children(child))

        return children

    @property
    def view(self) -> dict[str, Any]:
        if isinstance(self.state, DlgText):
            return {'speaker': self.state.speaker,
                    'text': self.state.text,
                    'responses': tuple(self._children(self.state).values())}

        return {'speaker': '',
                'text': '',
                'responses': tuple()}

    def transition(self, node: DlgNode, fsm_input=None):
        if self.state:
            fsm_input = fsm_input or 0
            if children := tuple(self._children(node)):
                selected = children[fsm_input if fsm_input <
                                    len(children) else 0]

                if not isinstance(selected, DlgEnd):
                    return selected

        return None

    def _on_enter(self, node: DlgNode):
        if isinstance(node, (DlgBranch, DlgEnd)):
            self.next()

    def viewListener(self, on_update: Callable[[dict[str, Union[str, tuple[Any]]]], None]):
        def listener():
            if isinstance(self.state, DlgText):
                on_update(self.view)

            if self.state is None:
                on_update({})

        return listener
