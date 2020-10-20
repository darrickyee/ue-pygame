
# %%
from typing import Any, Callable, Optional
import rx.operators as ops
from rx.subject.subject import Subject


# %%

State = Any
StateInput = Any

StateTransition = Callable[[State, StateInput], State]

# %%


def defaultTransition(state: State, state_input: StateInput = None) -> State:
    return None if state is None else state_input


FSM_START = object()
FSM_STOP = object()


class StateMachine:

    def __init__(self, initial_state: State,
                 transition: StateTransition = defaultTransition) -> None:
        self._init_state: State = initial_state
        self._state: State = initial_state

        self.transition: StateTransition = transition

        self._subject: Optional[Subject] = None
        self.onenter = None
        self.onexit = None
        self.onstart = None
        self.onstop = None
        self._init_events()

        self._started = False

    @property
    def state(self):
        return self._state

    @property
    def active(self):
        return self._started and not self._subject.is_disposed

    def _init_events(self):
        self._subject = Subject()
        self.onenter = self._subject.pipe(
            ops.filter(lambda e: e[0] == 'ENTER'))
        self.onexit = self._subject.pipe(
            ops.filter(lambda e: e[0] == 'EXIT'))
        self.onstart = self._subject.pipe(
            ops.filter(lambda e: e[0] == 'START'))
        self.onstop = self._subject.pipe(
            ops.filter(lambda e: e[0] == 'STOP'))

    def _send_event(self, event, state_input=None):
        data = {'state': self._state,
                'state_input': state_input,
                'fsm': self}
        self._subject.on_next((event, data))

    def next(self, state_input=None):
        if self.active:
            next_state = self.transition(self._state, state_input)
            if next_state is None:
                self.stop(state_input)
            else:
                self._send_event('EXIT', state_input)
                self._state = next_state
                self._send_event('ENTER', state_input)
        else:
            raise UserWarning('State machine is not active.')

    def start(self, state=None):
        # Restarting an active FSM disposes observable
        self.stop()
        self._state = self._init_state if state is None else state
        self._started = True
        self._send_event('START')
        self._send_event('ENTER')

    def stop(self, state_input=None):
        if self.active:
            self._send_event('EXIT', state_input)
            self._state = None
            self._started = False
            self._send_event('STOP')
            self._subject.on_completed()
            self._subject.dispose()
            self._init_events()

    def __repr__(self) -> str:
        status = f'state={self.state}' if self.active else 'INACTIVE'
        return f'{self.__class__.__name__}<{status}>'


# %%
sm = StateMachine('a')
sm._subject.subscribe(print, on_completed=lambda: print('Completed'))
# %%
