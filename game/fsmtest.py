# %%
import rx.operators as ops
from game.lib import StateMachine, FsmTransitionMap, to_observable
from game.lib.fsm import from_map

# %%
TMAP1: FsmTransitionMap = {
    ('bed', 'wake'): 'home',
    ('home', 'sleep'): 'bed',
    ('home', 'commute'): 'work',
    ('work', 'commute'): 'home',
}

TMAP2: FsmTransitionMap = {
    ('solid', 'heat'): 'liquid',
    ('liquid', 'cool'): 'solid',
    ('liquid', 'heat'): 'gas',
    ('gas', 'cool'): 'liquid'
}


def printEnter(event: dict):
    if event['event_type'] == 'ENTER':
        print(
            f"Received input {event['fsm_input']}.  New state is {event['state']}.")


SM = StateMachine('solid', transition=from_map(TMAP2))

EVENTS = to_observable(SM).pipe(ops.distinct_until_changed())
# %%
