import json
from rx.subject.subject import Subject
import rx.operators as ops
from .core.store import Store
from .core.fsm import changeListener

INITSTATE = {
    'dialogue': {'speaker': '',
                 'text': '',
                 'responses': []}
}

GAMESTATE = Store(INITSTATE)

EVENT_STREAM = Subject()

GAMESTATE.subscribe(changeListener(GAMESTATE, on_enter=lambda state: EVENT_STREAM.on_next(
    {'event_type': 'STATE_CHANGED', 'data': json.dumps(state)})))

ACTION_STREAM = EVENT_STREAM.pipe(
    ops.filter(lambda e: e['event_type'] == 'ACTION'), ops.map(lambda e: e['data']))

ACTION_STREAM.subscribe(GAMESTATE.dispatch)
