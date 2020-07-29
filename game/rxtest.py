# %%
import dataclasses as dc
from inspect import Parameter as par, Signature as sig
from functools import wraps, partial
import typing as T
import rx
import rx.operators as rxops
from rx.subject import Subject
from collections import UserList
import jsonpatch as jp
# from .graph import Graph, GLOBALVAL

# %%

sender = Subject()
dispatch = sender.on_next

closer = Subject()
events = sender.pipe(rxops.buffer(
    closer))


def nx():
    closer.on_next(True)


def process(evts):
    print(evts)
    for event in evts:
        if isinstance(event, int):
            print(event)
            if event < 5:
                dispatch(event + 5)


events.subscribe(process)
sender.subscribe(lambda e: print(f'Sender received {e}'))
# %%


TYPES_SIMPLE = (bool, int, float, str)
TYPES_COMPLEX = (list, tuple, dict)


class MissingType:

    def __bool__(self):
        return False


MISSING = MissingType()

# %%

# {'__contains__',
#  '__delitem__',
#  '__doc__',
#  '__eq__',
#  '__ge__',
#  '__getattribute__',
#  '__getitem__',
#  '__gt__',
#  '__hash__',
#  '__init__',
#  '__iter__',
#  '__le__',
#  '__len__',
#  '__lt__',
#  '__ne__',
#  '__new__',
#  '__repr__',
#  '__reversed__',
#  '__setitem__',
#  '__sizeof__',
#  'clear',
#  'copy',
#  'pop'}


def monitor(fn, obj=None):

    @wraps(fn)
    def _f(*args, **kwargs):
        if obj:
            old = obj.data.copy()

        val = fn(*args, **kwargs)

        if obj and old != obj.data:
            obj._dispatch(('update', jp.make_patch(old, obj.data).patch))

        return val

    return _f


class MyList(UserList):

    def __init__(self, initlist=None):
        super().__init__(initlist)
        self._subject = Subject()

    def _dispatch(self, event):
        self._subject.on_next(event)

    def __getattribute__(self, name):
        val = super().__getattribute__(name)

        if name in ('__setitem__',
                    'append',
                    'insert',
                    'pop',
                    'remove',
                    'clear',
                    'reverse',
                    'sort',
                    'extend'):
            return monitor(val, self)

        return val


ml = MyList([3, 4, ['a']])
ml._subject.subscribe(print)
ml[1] = 2


@dc.dataclass
class Event:
    target: T.Any
    op: str
    path: str = '/'
    value: T.Any = None
    oldvalue: T.Any = None


class ObservableMixin:

    def _setup(self):
        self._subject = Subject()
        self.subscribe = self._subject.subscribe
        self.pipe = self._subject.pipe

    def _dispatch(self, event):
        op, path, value, obj = event
        self._subject.on_next(Event(obj, op, path, value))

    def _add(self, prop, value):
        self._dispatch(('add', prop, value, self))

    def _delete(self, prop, oldvalue):
        self._dispatch(('delete', prop, oldvalue, self))

    def _read(self, prop, value):
        self._dispatch(('read', prop, value, self))

    def _update(self, prop, value, oldvalue):
        self._dispatch(('update', prop, value, self))


def isValidType(obj):
    return isinstance(obj, (*TYPES_SIMPLE, ObservableMixin))


class ContainerMixin(ObservableMixin):

    def __getitem__(self, key):
        value = super().__getitem__(key)
        self._read(key, value)
        return value

    def __setitem__(self, key, value):
        if not isValidType(value):
            raise TypeError(f'Invalid type {type(value).__name__}')

        try:
            oldvalue = super().__getitem__(key)
        except KeyError:
            oldvalue = MISSING

        super().__setitem__(key, value)
        if super().__getitem__(key) != oldvalue:
            self._update(key, value, oldvalue)

    def __delitem__(self, key):
        if key in self:
            oldvalue = super().__getitem__(key)
            self._delete(key, oldvalue)
        return super().__delitem__(key)

    def __repr__(self):
        return f"{type(self).__name__}({super().__repr__()})"


class ObsDict(ContainerMixin, dict):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup()


class ObsList(ContainerMixin, list):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._setup()

    def append(self, value):
        if not isValidType(value):
            raise TypeError(f'Invalid type {type(value).__name__}')
        self._add(len(self), value)
        return super().append(value)

    def extend(self, iterable):
        # Don't use append() since we don't want partial mutation
        if badtypes := set(type(item).__name__ for item in iterable if not isValidType(item)):
            raise TypeError(f'extend() contains invalid types: {badtypes}')

        return super().extend(iterable)


# %%


class Model:

    def __init__(self, **kwargs):
        self._subject = Subject()
        self.subscribe = self._subject.subscribe
        self.pipe = self._subject.pipe

        initvals = {prop: t()
                    for prop, t in type(self)._fields().items()}
        initvals.update({prop: val for prop, val in type(
            self).__dict__.items() if prop in type(self)._fields().items()})
        initvals.update(kwargs)

        self._cache = initvals

    @classmethod
    def _fields(cls):
        cls_ = cls
        fields = {}
        while issubclass(cls_, Model) and '__annotations__' in cls_.__dict__:
            fields.update(cls_.__annotations__)
            cls_ = cls_.__base__

        return fields

    def _dispatch(self, event):
        self._subject.on_next(event)

    def _read(self, name):
        value = object.__getattribute__(type(self), name)
        self._dispatch(('accessed', name, value))
        return value

    def _write(self, name, value):
        if value != self._cache.get(name, not value):
            self._cache[name] = value
            self._dispatch(('updated', name, value))

        return

    def __getattribute__(self, name):
        if name in type(self).__annotations__:
            return self._read(name)

        return super().__getattribute__(name)

    def __setattr__(self, name, value):
        if name in type(self).__annotations__:
            return self._write(name, value)

        return super().__setattr__(name, value)

    def __repr__(self):
        propstr = ', '.join(f"{prop}='{value}'" if isinstance(
            value, str) else f"{prop}={value}"
            for prop, value in self._cache.items())

        return f"{type(self).__name__}({propstr})"

    def __eq__(self, other):
        return type(self) == type(other) and self._cache == other._cache


def observe(obj: Model,
            listener: T.Callable[[Model], bool],
            event_type: str = None,
            prop: str = None):
    def efilter(e): return True if event_type is None else (e[0] == event_type)
    def pfilter(e): return True if prop is None else (e[1] == prop)

    return obj.pipe(
        rxops.filter(efilter),
        rxops.filter(pfilter)).subscribe(listener)


def observable(name, **prop_dict):

    methoddict = {}

    if isinstance(name, type):
        inclass: type = name
        name = inclass.__name__
        prop_dict = {**inclass.__annotations__, **{prop: value for prop,
                                                   value in inclass.__dict__.items()
                                                   if prop in inclass.__annotations__}}

        methoddict = {**inclass.__dict__, **methoddict}

    typedict = {prop: val if isinstance(val, type) else type(
        val) for prop, val in prop_dict.items()}

    valuedict = {prop: val() if isinstance(val, type)
                 else val for prop, val in prop_dict.items()}

    cls_ = type(name, (Model,), {'__annotations__': typedict,
                                 **methoddict, **valuedict})

    # Set signature if __init__ not overridden
    if '__init__' not in cls_.__dict__:
        params = [par(prop, par.POSITIONAL_OR_KEYWORD, default=valuedict[prop],
                      annotation=ann) for prop, ann in typedict.items()]

        cls_.__init__.__signature__ = sig(
            [par('self', par.POSITIONAL_OR_KEYWORD)] + params)

    return cls_

# %%


NewModel = observable('NewModel', x=3, y='hello', z=False)


@observable
class SecondModel:
    a: int = 32
    b: str = 'hlo'
    c: bool

    def madeit(self):
        print(f'Made {self.a}')


nm = NewModel()
sm = SecondModel()
# nm.subscribe(print)
# sm.subscribe(print)

d = observe(nm, print)

# %%


class Tester:

    def __init__(self, x):
        self._x = x
        self.observers = []

    def observe(self, observer, *args, **kwargs):
        self.observers.append(observer)

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if value != self._x:
            self._x = value
            for obs in self.observers:
                obs.on_next(self._x)


# %%
