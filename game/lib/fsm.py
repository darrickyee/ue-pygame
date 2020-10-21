
# %%
from typing import Any, Callable, Optional, TypedDict
import datetime

# %%

State = Any
StateInput = Any
StateEvent = TypedDict('StateEvent', event=str,
                       state=State, state_input=StateInput)

StateTransition = Callable[[State, StateInput], State]
StateAction = Callable[[StateEvent], None]
# %%


def defaultTransition(state: State, state_input: StateInput = None) -> State:
    return None if state is None else state_input


def transitionFromMap(transition_map: dict[tuple[Any, Any], State]):
    def transition(state: State, state_input: StateInput):
        return transition_map.get((state, state_input), state)

    return transition


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: StateTransition = defaultTransition, action: Optional[StateAction] = None) -> None:
        self._state: State = initial_state
        self._action: Optional[StateAction] = action

        self.transition: StateTransition = transition

    @property
    def state(self):
        return self._state

    @property
    def action(self):
        return self._action

    @action.setter
    def action(self, new_action: StateAction):
        if not callable(new_action):
            raise TypeError(
                'action must be of type Callable[[StateEvent], None]')
        self._action = new_action

    def next(self, state_input=None):
        next_state = self.transition(self._state, state_input)

        if next_state != self.state:
            if self._action:
                self._action(
                    {'event': 'EXIT', 'state': self._state, 'state_input': state_input})
                self._action(
                    {'event': 'ENTER', 'state': next_state, 'state_input': state_input})

            self._state = next_state

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<state={self.state}>'


# %%
sm = StateMachine('a')  # %%


LOG = []


def makeLogger(log):

    def logAction(event):
        event.update({'time': datetime.datetime.now().strftime('%H:%M:%S')})
        log.append(event)

    return logAction


sm.action = makeLogger(LOG)
# %%
