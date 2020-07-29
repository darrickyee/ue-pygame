# %%
import dataclasses as dc
import json
import rx
import rx.operators as rxops
from rx.subject import Subject
# %%


class Value:

    def __init__(self, default=None):
        self._value = default
        self._name = ''

    def __set_name__(self, owner, name):
        print(f'Creating property {name} on class {owner}')
        self._name = name

    def __get__(self, instance, owner=None):
        print(
            f'Accessed {self._name} on instance {owner}:{instance} with value {self._value}')
        if hasattr(instance, '_subject'):
            instance._subject.on_next(('accessed', self._name, self._value))
        return self._value

    def __set__(self, instance, value):
        if value != self._value:
            print(f'Setting {self._name} on instance {instance} to {value}')
            if hasattr(instance, '_subject'):
                instance._subject.on_next(
                    ('changed', self._name, self._value))
            self._value = value


class MyData:
    p1 = Value('Prop 1')
    p2 = Value('Prop 2')

    def __init__(self):
        self._subject = Subject()
        self.subscribe = self._subject.subscribe

    def observe(self, prop, listener):
        self._subject.pipe(rxops.filter(
            lambda item: item[1] == prop)).subscribe(listener)


md1 = MyData()


class MyData2:

    def __init__(self):
        self._subject = Subject()
        self.p1 = 'Prop 1'
        self.p2 = 'Prop 2'

    def __setattr__(self, name, value):
        if hasattr(self, '_subject') and getattr(self, name, None) != value:
            self._subject.on_next((self, name, value))
        super().__setattr__(name, value)

    def observe(self, name, *args, **kwargs):
        return self._subject.pipe(rxops.filter(lambda item: item[1] == name)).subscribe(*args, **kwargs)

    def subscribe(self, *args, **kwargs):
        return self._subject.subscribe(*args, **kwargs)


md2 = MyData2()

# %%

GS = {
    'level': 'Home',
    'target': None,
    'items': {},
    'tasks': {
        'Task1': {'completed': False}
    }
}


def checkEvent():

    def isEvent(obj):
        return isinstance(obj, dict) and 'eventType' in obj

    return rxops.map(lambda item: item if isEvent(item) else {'eventType': 'INVALID'})


def eventFilter(event_type):
    return rx.pipe(rxops.filter(lambda event: event.get('eventType', None) == event_type))


def printListener(event):
    print(f'Event {event}')


def taskSystem(event):
    print(f'Completed task {event["data"][0]}!')


SYSTEM = Subject()

EVENTS = SYSTEM.pipe(checkEvent())

EVENTS.subscribe(printListener)


def moveSystem(event):
    if event.get('data', None):
        GS['level'] = event['data'][0]
        SYSTEM.on_next({'eventType': 'complete_task', 'data': event['data']})


def invalidType(*args, **kwargs):
    print('Warning: invalid event')


MOVE_EVENTS = EVENTS.pipe(eventFilter('move'))
INVALID_EVENTS = EVENTS.pipe(eventFilter('INVALID'))
TASK_EVENTS = EVENTS.pipe(eventFilter('complete_task'))
MOVE_EVENTS.subscribe(moveSystem)
INVALID_EVENTS.subscribe(invalidType)
TASK_EVENTS.subscribe(taskSystem)


def run():
    cmd = None
    while cmd != 'exit':
        cmd = input('Command: ')
        etype, *data = cmd.split()
        SYSTEM.on_next({'eventType': etype, 'data': data})

    SYSTEM.on_completed()


run()
# %%


@dc.dataclass
class Node:

    _node_id: str

    @property
    def node_id(self):
        return self._node_id


@dc.dataclass
class Edge:

    _edge_id: str
    from_id: str
    to_id: str

    @property
    def edge_id(self):
        return self._edge_id


class DataNode(Node):

    def __init__(self, nid):
        self.node_id = nid + 23


# %%
