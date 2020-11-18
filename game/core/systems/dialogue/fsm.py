from typing import Any
import rx.operators as ops
from ....lib import Graph, StateMachine, evaluate, on_change, ispredicate, to_observable
from .nodes import DlgBranch, DlgEnd, DlgGroup, DlgNode, DlgText


class Dialogue(StateMachine):

    def __init__(self, graph: Graph, context: Any = None) -> None:
        self._graph = graph
        self._context = context or {}
        super().__init__(tuple(self._graph)[0], self.transition)

        self._updates = to_observable(self).pipe(on_change())
        self._updates.subscribe(self._on_enter)

        self.views = self._updates.pipe(
            ops.filter(lambda s: isinstance(s, DlgText)),
            ops.map(self.view),
            ops.distinct_until_changed()
        )

    def _eval(self, predicate: dict[str, Any]) -> bool:
        """Evaluates `predicate` against `self._context`.
        """
        if self._context and ispredicate(predicate):
            try:
                return evaluate(self._context, predicate)
            except ValueError:
                pass

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

    def view(self, node: DlgNode = None):
        node = node or self.state
        if isinstance(node, DlgText):
            return {'speaker': self.state.speaker,
                    'text': self.state.text,
                    'responses': tuple(self._children(self.state).values()) or ['[End]']}

        return {}

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
        if isinstance(node, DlgBranch):
            self.send()
