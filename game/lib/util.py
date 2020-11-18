from functools import partial, wraps
from typing import Any, Container, Mapping
import jsonpointer as jptr


def curry(fn):
    num_args: int = fn.__code__.co_argcount

    @wraps(fn)
    def _curried(*args, **kwargs):

        if len(args) + len(kwargs) >= num_args:
            return fn(*args, **kwargs)

        return partial(fn, *args, **kwargs)

    return _curried


@curry
def pick(keys: Container[str], doc: Mapping[str, Any]):
    """Curried function returning a new dictionary containing
     the items with keys specified in `keys`, if they exist.

    """
    return {prop: doc[prop] for prop in doc if prop in keys}


@curry
def pluck(key: str, doc: Mapping[str, Any]):
    """Curried version of `doc[key]`.

    """

    return doc[key]


resolve_pointer = curry(jptr.resolve_pointer)

set_pointer = curry(jptr.set_pointer)
