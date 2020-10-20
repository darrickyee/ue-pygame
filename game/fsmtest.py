# %%
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # nopep8

from game.lib import StateMachine

# %%
TRANSITIONS = {
    ('bed', 'wake'): 'home',
    ('home', 'sleep'): 'bed',
    ('home', 'commute'): 'work',
    ('work', 'commute'): 'home',
}


def transitions(state, state_input):
    return TRANSITIONS.get((state, state_input), state)


def logState(state, fsm_input):
    print(f'Received input {fsm_input}.  New state is {state}.')


SM = StateMachine('bed', transition=transitions, onenter=logState)

# %%
