from abc import ABC, abstractmethod
from typing import Any


class FsmReader(ABC):

    def __init__(self, context: Any = None) -> None:
        self._context = context

    @property
    def context(self):
        return self._context

    @abstractmethod
    def transition(self, state, fsm_input=None):
        raise NotImplementedError

    @abstractmethod
    def action(self, event: dict[str, Any]) -> None:
        raise NotImplementedError

    def view(self, state):
        return state
