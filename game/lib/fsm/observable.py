# %%
from functools import partial
from typing import Union, cast
import rx
import rx.operators as ops
import jsonpointer as jp
from .fsm import StateMachine


def to_observable(fsm: StateMachine) -> rx.Observable:
    """Creates an `Observable` from a `StateMachine`.

    Args:

    fsm (StateMachine): State machine instance.

    Returns:

    rx.Observable: An observable that emits `fsm.state` whenever `fsm` receives an input.
    """

    def subscription(observer, _):
        return fsm.subscribe(lambda: observer.on_next(fsm.state))

    return rx.create(cast(rx.core.typing.Subscription, subscription))


def change_listener(fsm: Union[StateMachine, rx.Observable]):  # pylint: disable=unsubscriptable-object

    if not isinstance(fsm, rx.Observable):
        fsm = to_observable(fsm)

    return fsm.pipe(ops.distinct_until_changed())


def on_change(path: str = ''):
    """Applies `distinct_until_changed` to an observable stream.

    If `path` is provided, emitted items must be JSON-like objects, and `path` is a JSON pointer to
     the observed value.  `None` is returned if the pointer cannot be resolved.

    Args:

        path (str, optional): [description]. Defaults to ''.

    Returns:
        [type]: [description]
    """
    if path:
        return ops.distinct_until_changed(partial(jp.resolve_pointer, pointer=path, default=None))

    return ops.distinct_until_changed()
