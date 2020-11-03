# %%
import json
from typing import Any, Literal
from jsonpointer import set_pointer
from .fsm import StateMachine


def set_value(state, action: dict[Literal['path', 'value'], Any]):
    return set_pointer(state, action['path'], action['value'], inplace=False)


def apply_snapshot(state, action: dict[str, Any]):
    return action['snapshot']


ACTIONS = {
    'SET_VALUE': set_value,
    'APPLY_SNAPSHOT': apply_snapshot
}


def storeTransition(state, action: dict[Any, Any]):
    return ACTIONS[action['action_type'].upper()](state, action)


class Store(StateMachine):

    def __init__(self, initial: dict[str, Any] = None) -> None:
        super().__init__(initial or {}, transition=storeTransition)

    @ property
    def state(self):
        return json.loads(json.dumps(self._state))

    def dispatch(self, action: dict[Any, Any]):
        return super().next(action)

    def next(self, _):
        raise NotImplementedError(
            "Use 'dispatch' to dispatch an action on the store.")
