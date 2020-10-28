# %%
import json
from typing import Any
from jsonpatch import apply_patch
from .fsm import StateMachine


def storeTransition(state, action):
    patch = [{'op': 'replace', 'path': action['path'], 'value': action['value']}]
    return apply_patch(state, patch)


class Store(StateMachine):

    def __init__(self, initial: dict[str, Any]) -> None:
        super().__init__(initial, transition=storeTransition)

    @property
    def state(self):
        return json.loads(json.dumps(self._state))
