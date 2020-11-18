# %%
import json
from typing import Any, Dict
from jsonpointer import set_pointer
from .fsm import StateMachine


class Store(StateMachine):

    def __init__(self, initial: Dict[str, Any] = None) -> None:
        super().__init__(initial or {}, transition=lambda state, pointer: set_pointer(
            state,
            pointer['path'],
            pointer['value'],
            inplace=False
        )
        )

    @ property
    def state(self):
        return json.loads(json.dumps(self._state))

    def update(self, path: str, value: Any):  # pylint: disable=unsubscriptable-object
        return super().send({'path': path, 'value': value})
