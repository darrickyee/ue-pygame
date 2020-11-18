from abc import ABC, abstractproperty
from typing import Any, Callable, Dict, cast
from .store import Store


class GameSystem(ABC):

    def __init__(self, context: Store) -> None:
        self._context = context
        self._locals = dict()

    @abstractproperty
    def actions(self) -> Dict[str, Callable[[Any], None]]:
        raise NotImplementedError

    def process(self, action: dict[str, Any]) -> None:
        if (cmd := action.get('action_type', None)) in self.actions:
            self.actions[cast(str, cmd)](action.get('data', None))
