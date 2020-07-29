# %%
from collections import UserList
import json
from functools import partial, wraps
import jsonpatch as jp
import rx.operators as op
from rx.subject import Subject

simple_types = (type(None), bool, int, float, str)


class IProperty:

    def __init__(self, value, types=None):
        self.types = types or (value if isinstance(
            value, type) else type(value))
        self.initval = value if not isinstance(value, type) else value()
        self.name = None
        self.subject = Subject()

    def observe(self, *args, **kwargs):
        return self.subject.subscribe(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        return obj.__dict__.setdefault(self.name, self.initval)

    def __set__(self, obj, value):
        # if not isinstance(value, self._type):
        #     raise TypeError(
        #         f"Property '{type(obj).__name__}.{self.name}' requires type '{self._type.__name__}'")
        oldval = obj.__dict__.get(self.name, self.initval)
        if oldval != value:
            obj.__dict__[self.name] = value
            self.subject.on_next(jp.make_patch(
                {self.name: oldval}, {self.name: value}).patch)

    def __set_name__(self, owner, name):
        self.name = name


class Tester:
    a = IProperty(0)
    d = IProperty(str)

    def __init__(self, a=0):
        self.a = a
        for prop in 'a', 'd':
            type(self).__dict__[prop].observe(self._write)

    def _write(self, item):
        print(item)


def asdict(obj):
    return {prop: getattr(obj, prop) for prop in ('a', 'd')}


LKEYS = {'__add__',
         '__class__',
         '__contains__',
         '__delattr__',
         '__delitem__',
         '__dir__',
         '__doc__',
         '__eq__',
         '__format__',
         '__ge__',
         '__getattribute__',
         '__getitem__',
         '__gt__',
         '__hash__',
         '__iadd__',
         '__imul__',
         '__init__',
         '__init_subclass__',
         '__iter__',
         '__le__',
         '__len__',
         '__lt__',
         '__mul__',
         '__ne__',
         '__new__',
         '__reduce__',
         '__reduce_ex__',
         '__repr__',
         '__reversed__',
         '__rmul__',
         '__setattr__',
         '__setitem__',
         '__sizeof__',
         '__str__',
         '__subclasshook__',
         'append',
         'clear',
         'copy',
         'count',
         'extend',
         'index',
         'insert',
         'pop',
         'remove',
         'reverse',
         'sort'}

DKEYS = {'__class__',
         '__contains__',
         '__delattr__',
         '__delitem__',
         '__dir__',
         '__doc__',
         '__eq__',
         '__format__',
         '__ge__',
         '__getattribute__',
         '__getitem__',
         '__gt__',
         '__hash__',
         '__init__',
         '__init_subclass__',
         '__iter__',
         '__le__',
         '__len__',
         '__lt__',
         '__ne__',
         '__new__',
         '__reduce__',
         '__reduce_ex__',
         '__repr__',
         '__reversed__',
         '__setattr__',
         '__setitem__',
         '__sizeof__',
         '__str__',
         '__subclasshook__',
         'clear',
         'copy',
         'fromkeys',
         'get',
         'items',
         'keys',
         'pop',
         'popitem',
         'setdefault',
         'update',
         'values'}

SKEYS = {'__and__',
         '__class__',
         '__contains__',
         '__delattr__',
         '__dir__',
         '__doc__',
         '__eq__',
         '__format__',
         '__ge__',
         '__getattribute__',
         '__gt__',
         '__hash__',
         '__iand__',
         '__init__',
         '__init_subclass__',
         '__ior__',
         '__isub__',
         '__iter__',
         '__ixor__',
         '__le__',
         '__len__',
         '__lt__',
         '__ne__',
         '__new__',
         '__or__',
         '__rand__',
         '__reduce__',
         '__reduce_ex__',
         '__repr__',
         '__ror__',
         '__rsub__',
         '__rxor__',
         '__setattr__',
         '__sizeof__',
         '__str__',
         '__sub__',
         '__subclasshook__',
         '__xor__',
         'add',
         'clear',
         'copy',
         'difference',
         'difference_update',
         'discard',
         'intersection',
         'intersection_update',
         'isdisjoint',
         'issubset',
         'issuperset',
         'pop',
         'remove',
         'symmetric_difference',
         'symmetric_difference_update',
         'union',
         'update'}

# %%

MUTPROPS = {
    'common': ['__delitem__', '__setitem__', 'clear', 'pop'],
    list: ['__iadd__', '__imul__',
           'append', 'extend', 'insert',
           'remove', 'reverse', 'sort'],
    dict: ['popitem', 'setdefault', 'update']
}


def mutator(fn):

    @wraps(fn)
    def mutate(obj, *args, **kwargs):
        oldval = obj.copy()
        result = fn(obj, *args, **kwargs)

        if obj != oldval and hasattr(obj, '_write'):
            obj._write(obj, oldval)

        return result

    return mutate


class IObservable:

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._subject = Subject()
        self.onWrite = self._subject.pipe(op.filter(
            lambda item: item[0] == 'write'),
            op.map(lambda item: (item[1], item[2]))).subscribe
        self.onPatch = self._subject.pipe(
            op.map(lambda item: jp.make_patch(item[2], item[1]))).subscribe
        self._disp = list()

    def __repr__(self):
        return f'{type(self).__name__}({self.copy()})'

    def _write(self, value, oldvalue):
        for disp in self._disp:
            disp.dispose()

        values = self.values() if hasattr(self, 'values') else self
        for val in values:
            if hasattr(val, 'onWrite'):
                self._disp.append(val.onWrite(
                    lambda item: self._write(value, oldvalue)))

        self._subject.on_next(('write', value, oldvalue))


def complextype(base):

    CLS = type(f'Obs{base.__name__.capitalize()}',
               (IObservable, base,), {})

    for prop in MUTPROPS['common'] + MUTPROPS.get(base, []):
        setattr(CLS, prop, mutator(base.__dict__[prop]))

    return CLS


ObsList = complextype(list)
ObsDict = complextype(dict)


# %%


def pluck(prop):
    def _get(obj):
        return getattr(obj, prop)

    return _get


class Model:

    def __init__(self, p1=0, p2='a'):
        self._subject = Subject()
        self.subscribe = self._subject.subscribe
        self.pipe = self._subject.pipe
        self._p1 = p1
        self._p2 = p2

    @ property
    def p1(self):
        return self._p1

    @ p1.setter
    def p1(self, value):
        if value != self._p1:
            self._p1 = value
            self._write('p1', value)

    @ property
    def p2(self):
        return self._p2

    @ p2.setter
    def p2(self, value):
        if value != self._p2:
            self._p2 = value
            self._write('p2', value)

    def _write(self, prop, value):
        self._subject.on_next(self)

    def _toJSON(self):
        return {prop: getattr(self, prop) for prop in ('p1', 'p2')}


def isP1Odd(model):
    return bool(model.p1 % 2)


def observe(obj, prop, observer=None):
    stream = obj.pipe(op.map(pluck(prop)), op.distinct_until_changed())
    if observer:
        return stream.subscribe(observer)

    return stream


m = Model()
# m.subscribe(print)
m.pipe(op.map(isP1Odd), op.distinct_until_changed()).subscribe(print)

# %%
