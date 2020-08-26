from typing import Dict, Iterable
import operator as op


def omit(keys: Iterable[str], d: Dict):
    return {key: d[key] for key in d if key not in keys}


def pick(keys: Iterable[str], d: Dict):
    return {key: d[key] for key in keys}

def eval_condition(left, relation, right):
    return getattr(op, relation, lambda x, y: True)(left, right)