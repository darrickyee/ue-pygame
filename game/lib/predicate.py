# %%
import operator
from functools import partial
from typing import Any, Literal
from collections.abc import Iterable, Mapping
import jsonpointer as jptr


OPS1 = {
    'contains': operator.contains,
    'eq': operator.eq,
    'ge': operator.ge,
    'gt': operator.gt,
    'le': operator.le,
    'lt': operator.lt,
    'ne': operator.ne,
    '==': operator.eq,
    '>=': operator.ge,
    '>': operator.gt,
    '<=': operator.le,
    '<': operator.lt,
    '!=': operator.ne,
    'in': lambda b, a: operator.contains(a, b)
}

OPS2 = {
    'and': all,
    'or': any,
    'not': lambda x: not any(x)
}


# %%


def _eval_firstorder(data: Any, predicate: Mapping):
    op, path, value = (predicate[k] for k in ('op', 'path', 'value'))

    try:
        return OPS1[op](jptr.resolve_pointer(data, path), value)
    except jptr.JsonPointerException as err:
        raise ValueError(
            f"Path '{path}' not found in object '{data}'") from err


def ispredicate(obj: Mapping[str, Any]):
    """Returns `1` if `obj` is a valid first-order predicate and `2` if `obj` is a valid
    second-order predicate.  Returns `False` otherwise.

    """
    if isinstance(obj, Mapping):
        if all(k in obj for k in ('op', 'path', 'value')) and obj['op'] in OPS1 and isinstance(obj['path'], str):
            return 1

        if all(k in obj for k in ('op', 'apply')) and obj['op'] in OPS2 and isinstance(obj.get('path', ''), str) and isinstance(obj['apply'], Iterable):
            return 2

    return False


def evaluate(data: Any, predicate: Mapping) -> bool:
    """Evaluates whether or not the json-like object `data` satisfies the conditions
    expressed in `predicate`, where `predicate` is a json-like mapping (e.g., a `dict`)
    similar to that described in https://tools.ietf.org/html/draft-snell-json-test-07.

    'First-order' predicates must contain keys `'op'`, `'path'`, and `'value'`.
    `'path'` is a json pointer string.
    Supported `op`s are:
    `['contains', 'eq', 'ge', 'gt', 'le', 'lt', 'ne', '==', '>=', '>', '<=', '<', '!=', 'in']`

    'Second-order' predicates must contain keys `'op'` and `'apply'` and may optionally
    contain a `'path'`.  `'apply'` is a sequence of first-order or second-order predicates.
    If a `'path'` is included, it will be prepended to the `'path'` for each predicate in `'apply'`.
    The default `'path'` for second-order predicates is the empty string.  Supported `op`s
    are: `['and', 'or', 'not']`.

    Args:
        data (Any): An object that supports property access via `jsonpointer`,
        such as a nested `dict`.

        predicate {Mapping} -- A first-order or second-order predicate mapping.

    Raises:
        ValueError: Raised if `predicate` is invalid or if the
        predicate's `'path'` value cannot be resolved as a json-pointer
        against `data`.

    Returns:
        bool: Result of evaluating `predicate` against `data`.
    """

    order = ispredicate(predicate)
    if order == 1:
        return _eval_firstorder(data, predicate)

    if order == 2:
        children = tuple(predicate['apply'])

        if not all(ispredicate(child) for child in children):
            raise TypeError(
                f"Predicate {predicate} contains invalid predicate in 'apply'")

        return OPS2[predicate['op']](
            evaluate(
                data, {**child, 'path': predicate.get('path', '') + child.get('path', '')})
            for child in children
        )

    raise ValueError(f"Invalid predicate: {predicate}")


def combine(*predicates: Mapping[str, Any],
            op: Literal['and', 'or', 'not'] = 'and',
            path: str = '') -> dict[str, Any]:
    """Combines multiple predicates into a single second-order predicate with
    operator `op` and path `path`.

    Args:
        op (Literal[, optional): Second-order operator ('and', 'or', 'not'). Defaults to 'and'.
        path (str, optional): Defaults to ''.

    Raises:
        TypeError: If any object in `predicates` is not a valid predicate.
        ValueError: If `op` is not a valid second-order operator.

    Returns:
        dict: A second-order operator whose `'apply'` value is `predicates`.
    """

    for predicate in predicates:
        if not ispredicate(predicate):
            raise TypeError(f"Invalid predicate received: '{predicate}'")

    if op not in OPS2:
        raise ValueError(
            f"Invalid aggregate predicate operator: '{op}' (must be one of {list(OPS2)})")

    return {'op': op, 'path': path, 'apply': list(predicates)}


def bind_data(data: Any):
    return partial(evaluate, data)


# %%
teststate = {
    'world': {
        'day': 3,
        'time': 'Morning',
        'location': 'Home'
    },
    'player': {
        'name': 'MC',
        'stat1': 23
    }


}

p1 = {
    'op': 'ge',
    'path': '/world/day',
    'value': 3
}

p2 = {
    'op': 'or',
    'path': '/player',
    'apply': [{
        'op': 'le',
        'path': '/stat1',
        'value': 3
    },
        {
        'op': '==',
        'path': '/name',
        'value': 'MC'
    },
        {'op': 'and', 'apply': [{'op': 'ne', 'path': '/name', 'value': 'Bob'}]}]
}

print(evaluate(teststate, p1))
print(evaluate(teststate, p2))

# %%
