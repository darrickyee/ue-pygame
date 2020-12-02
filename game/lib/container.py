# %%
import json
from abc import ABC, abstractproperty, abstractmethod
from functools import wraps
from typing import Any, Mapping
import rx.operators as ops
from rx.subject.subject import Subject
from rx.disposable.disposable import Disposable

# %%


def notifier(fn):
    @wraps(fn)
    def notify(obj, *args, **kwargs):
        val = fn(obj, *args, **kwargs)
        obj._notify()
        return val

    return notify


def copier(fn):

    @wraps(fn)
    def copy(obj, *args, **kwargs):
        return type(obj)(fn(obj, *args, **kwargs))

    return copy


class ObsBase(ABC):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._subject = Subject()
        self.subscribe = self._subject.pipe(
            ops.distinct_until_changed(json.dumps)).subscribe
        self._observables: dict[Disposable, Any] = {}

    @ abstractproperty
    def _values(self) -> tuple[Any, ...]:
        raise NotImplementedError

    def _notifier(self, fn):
        @ wraps(fn)
        def notify(*args, **kwargs):
            val = fn(*args, **kwargs)
            self._notify()
            return val

        return notify

    def _notify(self):
        self._update_observables()
        self._subject.on_next(self)

    def _update_observables(self):
        to_dispose = tuple(disposer
                           for disposer, value in self._observables.items()
                           if value not in self._values)
        for disposer in to_dispose:
            disposer.dispose()
            self._observables.pop(disposer)

        to_subscribe = (value
                        for value in self._values
                        if value not in self._observables.values() and isinstance(value, ObsBase))
        for new_value in to_subscribe:
            disposer = new_value.subscribe(lambda _: self._notify())
            self._observables[disposer] = new_value

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}({super().__repr__()})'


class ObsList(ObsBase, list):

    @property
    def _values(self):
        return tuple(self)


class ObsDict(ObsBase, dict):

    @property
    def _values(self) -> tuple[Any, ...]:
        return tuple(self.values())

# %%


MUTATORS = {
    ObsList: ['__iadd__', '__imul__', 'append', 'extend',
              'insert', 'remove', 'reverse', 'sort'],
    ObsDict: ['__ior__', 'popitem', 'setdefault', 'update']
}

COPIERS = {
    ObsList: ['__add__', '__mul__', '__rmul__'],
    ObsDict: ['__or__', '__ror__']
}

for cls in ObsList, ObsDict:
    for name in ['__delitem__', '__setitem__', 'clear', 'pop'] + MUTATORS[cls]:
        setattr(cls, name, notifier(getattr(cls, name)))

    for name in ['copy'] + COPIERS[cls]:
        setattr(cls, name, copier(getattr(cls, name)))

# %%
cmp1 = ObsDict(a=32, b='abc')
cmp1.subscribe(lambda d: print(f'Changed: {d}'))
cmp2 = ObsDict(d='hello')
cmp1['c2'] = cmp2
lst1 = ObsList()
cmp1['l1'] = lst1
# %%
