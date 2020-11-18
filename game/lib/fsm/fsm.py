
# %%
from typing import Any, Callable
from .types import State, FsmInput, FsmTransition
from .transitions import from_input


class FsmError(Exception):
    pass


class InvalidActionError(FsmError, TypeError):
    pass


class InvalidTransitionError(FsmError, TypeError):
    pass


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: FsmTransition = from_input) -> None:
        self._initial_state: State = initial_state
        self._state: State = initial_state
        self._listeners: dict[Callable[[], None], Any] = {}
        self.dispose = self._listeners.clear

        self.set_transition(transition)

    @ property
    def state(self):
        return self._state

    def send(self, fsm_input: FsmInput = None):

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
            disposer = self._disposer(listener)
            self._listeners[listener] = disposer
            return disposer

        raise TypeError(
            f"Cannot add listener: object '{listener}' is a valid listener.")

    def set_transition(self, transition: FsmTransition):
        if callable(transition):
            self._transition = transition
            return

        raise InvalidTransitionError(
            "Transition must be a callable with signature '(State, FsmInput) -> State'.")

    def _disposer(self, listener):
        def dispose():
            self._listeners.pop(listener, None)

        return dispose

    def _notify(self):
        for listener in tuple(self._listeners):
            listener()

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}<state={self.state}>'
