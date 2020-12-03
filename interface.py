# %%
import json
import ue_pylink as ue


def DispatchUE(event: dict):
    ue.log(f'Event: {event}')
    ue.dispatch('STATE_UPDATED',
                json.dumps(event))


def GetState(_: None):
    return json.dumps({})


def OnAction(action: str):
    ue.log(f'Action received: {action}')
