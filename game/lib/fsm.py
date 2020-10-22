
# %%
from typing import Any, Callable, Dict, Mapping, Optional, Tuple


# %%

State = Any
FsmInput = Any
FsmEvent = Dict[str, Any]


FsmTransition = Callable[[State, FsmInput], State]
FsmAction = Callable[[FsmEvent], None]
FsmTransitionMap = Mapping[Tuple[State, FsmInput], State]

# %%


class FsmError(Exception):
    pass


class InvalidActionError(FsmError, TypeError):
    pass


class InvalidTransitionError(FsmError, TypeError):
    pass

# %%


def identityTransition(_: State, fsm_input: FsmInput = None) -> State:
    return fsm_input


def transitionFromMap(transition_map: FsmTransitionMap):

    def transition(state: State, fsm_input: FsmInput):
        return transition_map.get((state, fsm_input), state)

    return transition


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: FsmTransition = identityTransition, action: Optional[FsmAction] = None) -> None:  # pylint: disable=unsubscriptable-object
        self._state: State = initial_state

        self.set_transition(transition)
        self.set_action(action)

    @ property
    def state(self):
        return self._state

    @ property
    def action(self) -> Optional[FsmAction]:  # pylint: disable=unsubscriptable-object
        return self._action

    @ action.setter
    def action(self, value):
        self.set_action(value)

    @ property
    def transition(self) -> FsmTransition:
        return self._transition

    @ transition.setter
    def transition(self, value):
        self.set_transition(value)

    def set_action(self, action: FsmAction = None):
        if not action:
            self._action = None
            return

        if callable(action):
            self._action = action
            return

        raise InvalidActionError(
            "Action must be a callable with signature '(StateEvent) -> None'.")

    def set_transition(self, transition: FsmTransition):
        if callable(transition):
            self._transition = transition
            return

        raise InvalidTransitionError(
            "Transition must be a callable with signature '(State, StateInput) -> State'.")

    def _on_action(self, event_type, **kwargs):
        if self.action:
            self._action({'event_type': event_type,
                          'state': self.state, **kwargs})

    def next(self, fsm_input=None):

        self._on_action('INPUT', fsm_input=fsm_input)

        next_state = self._transition(self._state, fsm_input)

        if next_state != self.state:
            self._on_action('EXIT', fsm_input=fsm_input)
            self._state = next_state
            self._on_action('ENTER', fsm_input=fsm_input)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<state={self.state}>'
