from functools import reduce, wraps
from typing import List, Tuple, Union
from warnings import warn

from .managers import EntityManager


EVENT_NONE = {'event_type': None}


def handler(event_types: Union[List[str], Tuple[str], str] = None):
    if event_types:
        event_types = (event_types,) if isinstance(
            event_types, str) else event_types

    def _handler(fn):

        @wraps(fn)
        def _fn(event, context=None):
            if not isinstance(event, dict):
                event = EVENT_NONE

            if event_types is None or event.get('event_type', None) in event_types:
                return fn(event, context) or event

            return event

        return _fn

    return _handler


class System():

    def __init__(self, handlers: List = None, entitymgr=None):
        self.handlers = handlers or []
        self.events = []
        self.entitymgr: EntityManager = entitymgr

    def _gethandler(self, obj):
        if hasattr(obj, 'process'):
            return obj.process

        if callable(obj):
            return obj

        warn(f"Handler '{obj}' is not valid; returning default handler")

        return lambda event, context: event

    def process(self, event, context=None):
        context = context or self
        return reduce(lambda event, handler: self._gethandler(handler)(event, context),
                      self.handlers,
                      event)

    def dispatch(self, event, context=None):
        context = context or self
        self.events = [*self.events, {'event': event, 'context': context}]

        if len(self.events) == 1:
            while self.events:
                self.process(**self.events[0])
                self.events = self.events[1:]
