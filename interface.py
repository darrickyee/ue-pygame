# %%
import json
from game import GAME
import ue_pylink as ue


def DispatchUE(event: dict):
    ue.log(f'Event: {event}')
    ue.dispatch('STATE_UPDATED',
                json.dumps(event))


GAME.events.subscribe(DispatchUE)
GAME.log = lambda a: ue.log(f'Received action: {a}')


def GetState(_: None):
    return json.dumps(GAME.state)


def OnAction(action: str):
    try:
        GAME.dispatch(json.loads(action))
    except json.decoder.JSONDecodeError:
        ue.log(f"Warning: Action '{action}' could not be processed.")
