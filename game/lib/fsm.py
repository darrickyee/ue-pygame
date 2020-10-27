
# %%
from typing import Any, Callable, Dict, Mapping, Optional, Sequence, Tuple


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


def inputTransition(_: State, fsm_input: FsmInput = None) -> State:
    """Sets the next state to the input value (ignores the current state).
    """
    return fsm_input


def transitionFromMap(transition_map: FsmTransitionMap):
    """Returns a transition function that implements the transitions specified 
    by `transition_map`.  The current state is returned if the `(state, fsm_input)` 
    is not found in the mapping's keys.

    Args:
        transition_map (FsmTransitionMap): A Mapping where each key is a `(state, fsm_input)` 
        tuple and its value is the corresponding next state.
    """

    def transition(state: State, fsm_input: FsmInput):
        return transition_map.get((state, fsm_input), state)

    return transition


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: FsmTransition = inputTransition, action: Optional[FsmAction] = None) -> None:  # pylint: disable=unsubscriptable-object
        self._initial_state: State = initial_state
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
            self._action = lambda _: None
            return

        if callable(action):
            self._action = action
            return

        raise InvalidActionError(
            "Action must be a callable with signature '(FsmEvent) -> None'.")

    def set_transition(self, transition: FsmTransition):
        if callable(transition):
            self._transition = transition
            return

        raise InvalidTransitionError(
            "Transition must be a callable with signature '(State, FsmInput) -> State'.")

    def _event(self, event_type, **kwargs):
        return {'event_type': event_type,
                'state': self.state, 'target': self, **kwargs}

    def next(self, fsm_input=None):

        next_state = self._transition(self._state, fsm_input)

        if next_state != self.state:
            self._action(self._event('EXIT', fsm_input=fsm_input))
            self._state = next_state
            self._action(self._event('ENTER', fsm_input=fsm_input))

    def reset(self):
        """Sets the state to the initial state and clears the `action` property.
        """
        self._state = self._initial_state
        self.action = None
        self._event('RESET')

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<state={self.state}>'
