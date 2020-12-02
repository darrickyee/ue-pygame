# %%
import json
from functools import wraps
from typing import Any, Callable, Optional, Type, Union
import rx.operators as ops
from rx.disposable.disposable import Disposable
from rx.subject.subject import Subject
from ..lib import GameSystem, to_observable, Store

# %%


# %%


class EcsStore(Store):

    @property
    def entities(self) -> dict[str, dict[str, Any]]:
        entities = {
            eid for comp in self.state for eid in self.state[comp]}
        return {eid: self.get_entity(eid) for eid in entities}

    def get_entity(self, entity_id: str) -> dict[str, Any]:
        components = {k: v[entity_id]
                      for k, v in self.state.items()
                      if entity_id in v}

        return components

    def get_component(self, entity_id: str, component: str):
        return self.state.get(component, {}).get(entity_id, None)

    def set_component(self, entity_id: str, component: str, value: Any):
        self.update(f'/{component}/{entity_id}', value)

    def select_entities(self, component_filter: Union[str, tuple[str, ...]]) -> dict[str, Any]:

        if not isinstance(component_filter, tuple):
            component_filter = (component_filter, )

        return {eid: components
                for eid, components in self.entities.items()
                if all(comp in components for comp in component_filter)}


class EcsGameSystem(GameSystem):

    def __init__(self, store: EcsStore) -> None:
        super().__init__(store)
        self.store: EcsStore = store


class World:

    def __init__(self, store: EcsStore) -> None:
        self.log: Optional[Callable[[str], None]] = None
        self._store = store
        self.get_entity = self._store.get_entity
        self.select_entities = self._store.select_entities
        self._systems = {}
        self._actions = Subject()

        self._queue = []

        self.events = to_observable(self._store).pipe(
            ops.distinct_until_changed())

    @property
    def entities(self):
        return self._store.entities

    def dispatch(self, action):
        self._queue.append(action)
        while self._queue:
            self._actions.on_next(self._queue.pop(0))

    @property
    def state(self):
        return self._store.state

    @property
    def systems(self):
        return tuple(self._systems)

    def add_system(self, system_class: Type[GameSystem]):
        if system_class not in map(type, self.systems):
            system = system_class(self._store)
            disposer = self._actions.pipe(
                ops.filter(
                    lambda action: action.get(
                        'action_type', None) in system.actions
                )
            ).subscribe(system.process)
            self._systems[system] = disposer

        else:
            raise TypeError(
                f"World already contains a system of type '{system_class.__name__}'")

    def remove_system(self, system_class: Type[GameSystem]):
        systems = {s: d for s, d in self._systems.items()
                   if isinstance(s, system_class)}

        if systems:
            for system, disposer in systems.items():
                disposer.dispose()
                del self._systems[system]
        else:
            raise TypeError(
                f"World does not contain a system of type '{system_class.__name__}'")
