
# %%
from typing import Any, Callable, Dict, Mapping, Tuple


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

# %%


def changeListener(fsm: 'StateMachine', on_change: Callable[[dict], None] = None,
                   on_enter: Callable[[Any], None] = None,
                   on_exit: Callable[[Any], None] = None):
    """Returns a listener that invokes the provided callbacks when `fsm.state` changes.

    Args:

    `fsm` (StateMachine): The state machine whose state changes should be responded to.

    `on_change` (Callable[[dict], None], optional): Callback that will be passed a `dict`
                with keys `'enter'` and `'exit'` whose values are the last and current states, respectively. Defaults to None.

    `on_enter` (Callable[[Any], None], optional): Callback that will be passed the current state. Defaults to None.

    `on_exit` (Callable[[Any], None], optional): Callback that will be passed the previous state. Defaults to None.

    Returns:

    `listener` (Callable[[Any], None]): Callback to be passed to `StateMachine.subscribe()`.
    """

    current_state = fsm.state

    def handle_change():
        if any((on_change, on_enter, on_exit)):
            nonlocal current_state
            next_state = fsm.state
            if current_state != next_state:
                if callable(on_change):
                    on_change({'exit': current_state, 'enter': next_state})

                if callable(on_exit):
                    on_exit(current_state)

                if callable(on_enter):
                    on_enter(next_state)

                current_state = next_state

    return handle_change


def stateListener(fsm: 'StateMachine', on_input: Callable[[Any], None]):
    """Returns a listener that invokes the provided callback whenever `fsm` receives an input.

    Args:

    fsm (StateMachine): StateMachine whose inputs should be subscribed to.

    on_input (Callable[[Any], None]): Callback that will be passed the current state.

    Returns:

    `listener` (Callable[[Any], None]): Callback to be passed to `StateMachine.subscribe()`.
    """
    return lambda: on_input(fsm.state)


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: FsmTransition = inputTransition) -> None:
        self._initial_state: State = initial_state
        self._state: State = initial_state
        self._listeners: set[Callable[[], None]] = set()
        self.dispose = self._listeners.clear

        self.set_transition(transition)

    @ property
    def state(self):
        return self._state

    def next(self, fsm_input=None):

        next_state = self._transition(self._state, fsm_input)

        if next_state != self.state:
            self._state = next_state

        self._notify()

    def reset(self):
        """Sets the state to the initial state and clears all listeners.
        """
        self._state = self._initial_state
        self.dispose()

        self._notify()

    def subscribe(self, listener: Callable[[], None]):
        if callable(listener):
            self._listeners.add(listener)
            return self._disposer(listener)

        raise TypeError(
            f"Cannot add listener: object '{listener}' is not callable.")

    def set_transition(self, transition: FsmTransition):
        if callable(transition):
            self._transition = transition
            return

        raise InvalidTransitionError(
            "Transition must be a callable with signature '(State, FsmInput) -> State'.")

    def _disposer(self, listener):
        def dispose():
            try:
                self._listeners.remove(listener)
            except KeyError:
                pass

        return dispose

    def _notify(self):

        for listener in self._listeners.copy():
            listener()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<state={self.state}>'
