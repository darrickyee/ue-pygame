# %%
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # nopep8

from game.lib import StateMachine, transitionFromMap, FsmTransitionMap, State, FsmInput, FsmEvent

# %%
TRANSITIONS: FsmTransitionMap = {
    (State('bed'), FsmInput('wake')): State('home'),
    (State('home'), FsmInput('sleep')): State('bed'),
    (State('home'), FsmInput('commute')): State('work'),
    (State('work'), FsmInput('commute')): State('home'),
}


def printEnter(event: FsmEvent):
    if event['event_type'] == 'ENTER':
        print(
            f"Received input {event['fsm_input']}.  New state is {event['state']}.")


SM = StateMachine(State('bed'), transition=transitionFromMap(
    TRANSITIONS), action=printEnter)

# %%
