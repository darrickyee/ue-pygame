# %%
from game.core.store import Store
from game.core.fsm import changeListener
from game.core.predicate import evaluator
from rx.subject.subject import Subject
import rx.operators as ops

st = Store({'world': {'day': 1, 'location': 'Home'},
            'player': {'name': 'Bob', 'memories': ['ok', 'not ok']}})

# %%
st.update({'action_type': 'set_value', 'path': '/world/day', 'value': 34})

# %%
sub = Subject()
lst = changeListener(st, on_enter=sub.on_next)
st.subscribe(lst)

cond_stream = sub.pipe(ops.first(evaluator(
    {'path': '/world/day', 'op': 'gt', 'value': 35}))).subscribe(lambda x: print(f'Condition met: {x}'))

# %%


class QuestTask:
    def __init__(self, gamestore: Store, complete_conditions, failure_conditions, on_complete=None, on_failure=None, **kwargs) -> None:
        self._store = gamestore
        self.on_complete = on_complete
        self.on_failure = on_failure
