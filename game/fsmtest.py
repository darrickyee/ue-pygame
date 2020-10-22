# %%
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))  # nopep8

from game.lib import StateMachine, transitionFromMap, FsmTransitionMap, FsmEvent

# %%
TRANSITIONS: FsmTransitionMap = {
    ('bed', 'wake'): 'home',
    ('home', 'sleep'): 'bed',
    ('home', 'commute'): 'work',
    ('work', 'commute'): 'home',
}


def printEnter(event: FsmEvent):
    if event['event_type'] == 'ENTER':
        print(
            f"Received input {event['fsm_input']}.  New state is {event['state']}.")


SM = StateMachine('bed', transition=transitionFromMap(
    TRANSITIONS), action=printEnter)

# %%
