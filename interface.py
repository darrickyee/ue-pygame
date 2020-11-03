
import json
from json.decoder import JSONDecodeError
import jsonpointer as jptr
import rx.operators as ops
import ue_pylink as ue
from game import EVENT_STREAM, GAMESTATE


EVENT_STREAM.pipe(ops.filter(lambda value: value.get(
    'event_type', None) == 'STATE_CHANGED'),
    ops.map(lambda value: value['data'])).subscribe(lambda state: ue.dispatch('STATE_CHANGED', state))


def GetState(_: None):
    return json.dumps(GAMESTATE.state)


def SetState(newstate: str):
    EVENT_STREAM.on_next({'event_type': 'ACTION', 'data': {
                         'action_type': 'APPLY_SNAPSHOT', 'snapshot': json.loads(newstate)}})
