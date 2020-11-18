from abc import ABC, abstractmethod
from game import World


class System(ABC):

    actions = set()

    def __init__(self, world: World) -> None:
        self._world = world

    @abstractmethod
    def process(self, action):
        raise NotImplementedError
