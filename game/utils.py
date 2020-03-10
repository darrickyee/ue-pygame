from typing import Dict, Iterable


def omit(keys: Iterable[str], d: Dict):
    return {key: d[key] for key in d if key not in keys}


def pick(keys: Iterable[str], d: Dict):
    return {key: d[key] for key in keys}
