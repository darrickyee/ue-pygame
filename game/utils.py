from typing import Dict, Iterable


def omit(keys: Iterable, d: Dict):
    return {key: d[key] for key in d if key not in keys}


def pick(keys: Iterable, d: Dict):
    return {key: d[key] for key in keys}
