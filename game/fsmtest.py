# %%
from game.core.fsm import StateMachine, transitionFromMap, changeListener, stateListener, FsmTransitionMap, FsmEvent

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


def printEnter(event: FsmEvent):
    if event['event_type'] == 'ENTER':
        print(
            f"Received input {event['fsm_input']}.  New state is {event['state']}.")


SM = StateMachine('solid', transition=transitionFromMap(
    TMAP2))

# %%


# %%
